library(dplyr)
library(rvest)
library(utils)
library(downloader)
library(stringi)
library(arrow)


# Reading dataset (to continue downloading)
if(F){
    df <- read.csv("title.basics.tsv", header = T, sep = "\t", encoding = "UTF-8")
    df <- df[df$titleType == "movie" & df$genres != "//N",]
    df$main_genre <- gsub(",.*", "", df$genres)
    df$primaryTitle <- gsub("[^a-zA-Z0-9 á-űÁ-Ű]", "", df$primaryTitle)
    df$searched <- 0
    df$searched[df$primaryTitle %in% downloaded_subs] <- 1
    df <- arrange(df, searched)
    write_feather(df, "movie_titles.feather")
}

df <- read_feather("movie_titles.feather")
downloaded_subs <- list.files("./subtitles/") %>% 
                    gsub("\\(\\d\\d\\d\\d)\\.srt", "", .) %>% 
                    stri_trim()



##### Downloading subtitles
root <- "https://yifysubtitles.org"
url <- "https://yifysubtitles.org/search?q="
options(scipen = 999)


io_wait <- function(max=2){
    waited = 0
    if(length(list.files("./subtitles/temp/")) == 0 &
       waited <= max){
        Sys.sleep(0.1)
        waited = waited + 0.1
    }
}

unlink_temps <- function(){
    unlink(filedest)
    unlink("./subtitles/temp", recursive = T)
}

not_searched_rows <- nrow(df[df$searched == 0,])


for (i in 1:not_searched_rows){
    dir.create("./subtitles/temp", showWarnings = F)
    title <- df$primaryTitle[i]
    print(paste(round(i/not_searched_rows, 3), title, sep="    "))
    search <- URLencode(paste(url, title, sep=""))
    
    download_site <- tryCatch({
        
        subtitle_site <<- read_html(search) %>% 
                html_node(".media-body") %>%
                html_node("a") %>% html_attr("href") %>% paste(root, ., sep = "") %>% 
                read_html()
        
        s_title <<- subtitle_site %>% html_node(".movie-main-title") %>% html_text()
        
        if(i>1){df$searched[i] <- 1}
        
        subtitle_site %>% html_nodes(".table.other-subs") %>%
        html_nodes("a") %>% html_attr("href") %>% grep("subtitle.*eng", ., value = T) %>% .[1] %>% 
        paste(root, ., sep="") %>% read_html() %>% html_nodes(".download-subtitle") %>% 
        html_attr("href") %>% paste(root, ., sep="") %>% 
            return()
        
    }, error = function(e){
            NULL}
    )
    if(!is.null(download_site)){
        filedest <- paste("./subtitles/", title, ".zip", sep="")
        
        skip <- tryCatch({
            download(download_site, filedest, quiet=T)
            unzip(filedest, exdir = "./subtitles/temp")
            io_wait()
            unzipped <- list.files("./subtitles/temp/", full.names = T)
            new_name <- paste("./subtitles/", s_title, ".srt", sep="")
            file.rename(unzipped[1], new_name)
            unlink_temps()
            Sys.sleep(1)
            F 
        }, error = function(e){
            T}
        )
        if (skip){
            unlink_temps()
            next}
        }
}


