

eduflow_data = read.csv("Eduflow2_stats.csv")  # read csv file 

eduflow_data$score = as.numeric(sub(",", ".", eduflow_data$score, fixed = TRUE))

music = eduflow_data[eduflow_data$musique == 1,]
nomusic = eduflow_data[eduflow_data$musique == 0,]

wilcox.test(music$score, nomusic$score, paired=TRUE)

wilcox.test(music$score, nomusic$score)

boxplot(music$score, nomusic$score)

subset(eduflow_data, music == 1)