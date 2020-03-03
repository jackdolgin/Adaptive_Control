# install.packages("devtools")
if (!require(devtools)) install.packages("pacman")
pacman::p_load(googleLanguageR, googleCloudStorageR, tuneR, fs, data.table,
               DescTools, tidyverse, future, here, magrittr)
pacman::p_load_gh("LiKao/VoiceExperiment")

no_cores <- availableCores() - 1
plan(multicore, workers = no_cores)

"Authentication_File.json" %T>%
  gl_auth %>%
  gcs_auth

mypath <- here("Data")


predictive_context <- function(mydf, either_block_or_side, relevant_task,
                               na_tasks){
  mydf %>%
    group_by(Participant, !!either_block_or_side) %>%
    mutate(!!paste0(quo_name(either_block_or_side), "_Bias") := 
             case_when(
               Task %in% na_tasks ~ NA_character_,
               Task != relevant_task ~ "Neither",
               sum(trial_congruency == "Congruent") / n() > .5 ~ "Congruent",
               TRUE ~ "Incongruent")
    )
}

prep_data <- dir_ls(mypath, glob = "*.csv", recurse = TRUE) %>%
  map_dfr(fread) %>%
  filter(Trial > 0) %>%
  select(-Date) %>%
  left_join(fread("IPNP_spreadsheet_synonyms.csv")) %>%
  group_by(Participant) %>%
  mutate(
    trial_congruency = ifelse(Picture_Identity == Picture_Label,
                              "Congruent", "Incongruent"),
    End_recording = ifelse(
      lead(Stim_Onset) > Stim_Onset + 58 | row_number() == n(),
      Stim_Onset + 58,
      lead(Stim_Onset, default = last(Stim_Onset) + 58))) %>%
  predictive_context(quo(Block), 1, c(0)) %>%
  predictive_context(quo(Task_Side), 2, 0:1) %>%
  ungroup() %>%
  mutate_at(vars(Synonyms), ~paste(
    ., ifelse(Picture_Identity == Picture_Label,
              Picture_Label,
              paste(Picture_Identity, Picture_Label, sep = ", "))))

pull_in_from_google <- prep_data %>%
  pmap_df(function(Stim_Onset, Trial, End_recording,
                   Participant, Synonyms, ...){
    
    audio_path <- path(mypath, Participant, "audio",
                       paste0("Trial_", Trial, ".wav"))
    
    readWave(dir_ls(path(mypath, Participant, "audio", "full_recording"),
                    glob = "*.wav"),
             from = Stim_Onset, to = End_recording, units = "seconds") %>%
    writeWave(audio_path, extensible = FALSE)

    transcribed_list <- gl_speech(audio_path, sampleRateHertz = 44100L,
                                  speechContexts =
                                    list(phrases = strsplit(Synonyms, ',') %>%
                                           unlist %>%
                                           trimws))
    
    if (length(transcribed_list$timings) > 0){
      precise_timing <- audio_path %>% read.wav %>% onsets
      
      transcribed_list$transcript %>%
        mutate_at(vars(transcript), trimws) %>%
        mutate(
          Participant,
          Trial,
          preciseStartTime = pluck(precise_timing, first, "start"),
          preciseEndTime = pluck(precise_timing, last, "end"))
    }
  }) %>%
  right_join(prep_data) %T>%
  write.csv("pull_in_from_google.csv")


pull_in_from_google2 <- pull_in_from_google %>%
  group_by_at(vars(-preciseStartTime, -preciseEndTime, -transcript,             # so that each trial only takes up 1 row,...
                   -confidence)) %>%                                            # though each trial might only be one row...
  summarise(across(transcript, ~paste0(., collapse = "")),                      # anyways; depends on whether Google spits...
            across(preciseStartTime, min),                                      # out multiple rows for $transcript
            across(preciseEndTime, max)) %>%                                    
  ungroup() %>%
  mutate_at(vars(Picture_Identity, Picture_Label, Synonyms, transcript),
            ~str_remove_all(., " ") %>% tolower) %>%
  mutate(Accuracy = pmap_lgl(., function(
    Synonyms, transcript, Picture_Label, trial_congruency, ...){
    case_when(
      transcript == Picture_Label & trial_congruency == "Incongruent" ~ FALSE,
      transcript %in% pluck(strsplit(Synonyms, ','), 1) ~ TRUE,
      TRUE ~ NA)} 
  )) %>%
  filter(Accuracy)

Neutral_Timings <- pull_in_from_google2 %>%
  # filter(Task == 0) %>%     # need to uncomment this later, because neutral trials should only be extracted from Task == 0
  group_by(Picture_Identity) %>%
  summarise(RT = mean(preciseStartTime, na.rm = TRUE))

pull_in_from_google3 <- pull_in_from_google2 %>%
  filter(Task > 0,
         !is.na(preciseStartTime)) %>%
  mutate(
    RT_comparison = map_dbl(
      Picture_Identity,
      ~filter(Neutral_Timings, Picture_Identity == .) %>% pull(RT)),
    RT_diff = preciseStartTime - RT_comparison)


pull_in_from_google3 %>%
  group_by(Block_Bias, Task_Side_Bias, trial_congruency) %>%
  summarise(mean(RT_diff))

