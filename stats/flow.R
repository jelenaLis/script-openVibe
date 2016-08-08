

eduflow_data = read.csv("Eduflow2_stats.csv")  # read csv file 

eduflow_data$score = as.numeric(sub(",", ".", eduflow_data$score, fixed = TRUE))

music = eduflow_data[eduflow_data$musique == 1,]
nomusic = eduflow_data[eduflow_data$musique == 0,]

wilcox.test(music$score, nomusic$score, paired=TRUE)

wilcox.test(music$score, nomusic$score)

#boxplot(music$score, nomusic$score)

## perfs

# loading data and adding a column for eduflow
perf_data = read.csv("data.csv")
perf_data$eduflow = -1

# for overall score
perf_data$total = -1

ids = unique(perf_data$list_id)


for (id in ids) {
  cat("\n\nSujet ID:", id, "\n")
  mus_edu_score = eduflow_data[eduflow_data$ID == id & eduflow_data$musique == 1,]$score
  cat("music score", mus_edu_score, "\n")
  perf_data[perf_data$list_id == id & perf_data$list_cond == "mus",]$eduflow = mus_edu_score

  nomus_edu_score = eduflow_data[eduflow_data$ID == id & eduflow_data$musique == 0,]$score
  cat("nomusic score", nomus_edu_score, "\n")
  perf_data[perf_data$list_id == id & perf_data$list_cond == "nomus",]$eduflow = nomus_edu_score
  
  score_L_mus = mean(perf_data[perf_data$list_id == id & perf_data$list_cond == "nomus" & perf_data$list_direction == 0,]$list_score)
  score_R_mus = mean(perf_data[perf_data$list_id == id & perf_data$list_cond == "nomus" & perf_data$list_direction == 1,]$list_score)

}

aggregate(perf_data, list("list_id"), mean)


data_mean = aggregate( cbind(list_class, list_score, eduflow) ~ list_id + list_cond + list_direction, data = perf_data, FUN = mean)
 
data_mean[data_mean$list_direction == 0,]

# how score and classifier output relate
plot(data_mean$list_class, data_mean$list_score)

# reverse left classifier output
data_mean_bis = data_mean
data_mean_bis[data_mean_bis$list_direction == 0,]$list_class = data_mean_bis[data_mean_bis$list_direction == 0,]$list_class * -1

# score/classifier, no matter class
plot(data_mean_bis$list_class, data_mean_bis$list_score)


# average across left/right
data_across = aggregate( cbind(list_class, list_score, eduflow) ~ list_id + list_cond, data = data_mean_bis, FUN = mean)

# try to sense some sense
plot(data_across$list_class, data_across$list_score)
plot(data_across$list_score, data_across$eduflow)
plot(data_across$list_class, data_across$eduflow)



data_left = data_mean_bis[data_mean_bis$list_direction == 0,]
plot(data_left$list_score, data_left$eduflow)
plot(data_left$list_class, data_left$eduflow)

data_right = data_mean_bis[data_mean_bis$list_direction == 1,]
plot(data_right$list_score, data_right$eduflow)
plot(data_right$list_class, data_right$eduflow)

plot(data_across$list_score, data_across$eduflow)



  aggregate( list_class ~ list_id + list_cond, data = perf_data, FUN = mean)

## correlations

library(Hmisc)


rcorr(perf_data$score , type="pearson") 
