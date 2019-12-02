# Install packages if not already installed, then load them
if (!require(devtools)) install.packages("pacman")
pacman::p_load(googleLanguageR, googleCloudStorageR, fs, stringi, dplyr)

gl_auth("Testing1-d73486395f8e.json")
gcs_auth("Testing1-d73486395f8e.json")

bucketname <- "jacksbucket123"
gcs_create_bucket(bucketname, "airy-office-257300")
gcs_global_bucket(bucketname)

myattempt <-
  dir_ls(
    path = "/Users/jackdolgin/Box/My Job/Research/Studies/Following Yu-Chin/data",
    glob = "*.wav", recurse = TRUE) %>%
  as.character() %>%
  walk(~gcs_upload(., name = stri_extract_last_regex(., "[:digit:]+"))) %>%
  stri_extract_last_regex("[:digit:]+") %>%
  paste("gs:/", bucketname, ., sep = "/") %>%
  map(~gl_speech(., sampleRateHertz = 44100L, asynch = TRUE))

map(myattempt, gl_speech_op) %>%
  map_df(function(input) {
    gemnext <- tibble(input[1]) %>%
      unnest_legacy() %>%
      mutate_all(trimws)
    
    tibble(input[2]) %>%
      unnest_legacy() %>%
      unnest_legacy() %>%
      mutate_at(vars(startTime, endTime), list(~as.numeric(gsub("s", "", .)))) %>%
      right_join(gemnext, c("word" = "transcript"))
  })
