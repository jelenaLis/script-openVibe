

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

ids = unique(perf_data$list_id)


for (id in ids) {
  cat("\n\nSujet ID:", id, "\n")
  mus_edu_score = eduflow_data[eduflow_data$ID == id & eduflow_data$musique == 1,]$score
  cat("music score", mus_edu_score, "\n")
  perf_data[perf_data$list_id == id & perf_data$list_condition == "mus"]$eduflow = mus_edu_score

  nomus_edu_score = eduflow_data[eduflow_data$ID == id & eduflow_data$musique == 0,]$score
  cat("nomusic score", nomus_edu_score, "\n")
  perf_data[perf_data$list_id == id & perf_data$list_condition == "nomus"]$eduflow = nomus_edu_score

}