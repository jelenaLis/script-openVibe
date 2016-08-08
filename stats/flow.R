

eduflow_data = read.csv("Eduflow2_stats.csv")  # read csv file 

eduflow_data$score = as.numeric(sub(",", ".", eduflow_data$score, fixed = TRUE))
eduflow_data$score3D = as.numeric(sub(",", ".", eduflow_data$score3D, fixed = TRUE))


music = eduflow_data[eduflow_data$musique == 1,]
nomusic = eduflow_data[eduflow_data$musique == 0,]

wilcox.test(music$score, nomusic$score, paired=TRUE)

wilcox.test(music$score, nomusic$score)

#boxplot(music$score, nomusic$score)

## perfs

# loading data and adding a column for eduflow
perf_data = read.csv("data.csv")
perf_data$eduflow = -1
perf_data$eduflow3D = -1

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
  
  # 3D version
  mus_edu_score3D = eduflow_data[eduflow_data$ID == id & eduflow_data$musique == 1,]$score3D
  cat("music score3D", mus_edu_score3D, "\n")
  perf_data[perf_data$list_id == id & perf_data$list_cond == "mus",]$eduflow3D = mus_edu_score3D

  nomus_edu_score3D = eduflow_data[eduflow_data$ID == id & eduflow_data$musique == 0,]$score3D
  cat("nomusic score3D", nomus_edu_score3D, "\n")
  perf_data[perf_data$list_id == id & perf_data$list_cond == "nomus",]$eduflow3D = nomus_edu_score3D
}


data_mean = aggregate( cbind(list_class, list_score, eduflow, eduflow3D) ~ list_id + list_cond + list_direction, data = perf_data, FUN = mean)
 
# how score and classifier output relate
plot(data_mean$list_class, data_mean$list_score)

# reverse left classifier output
data_mean_bis = data_mean
data_mean_bis[data_mean_bis$list_direction == 0,]$list_class = data_mean_bis[data_mean_bis$list_direction == 0,]$list_class * -1

# score/classifier, no matter class
plot(data_mean_bis$list_class, data_mean_bis$list_score)

# average across left/right
data_across = aggregate( cbind(list_class, list_score, eduflow, eduflow3D) ~ list_id + list_cond, data = data_mean_bis, FUN = mean)

# try to sense some sense
plot(data_across$list_class, data_across$list_score)
plot(data_across$list_score, data_across$eduflow)
plot(data_across$list_class, data_across$eduflow)

## correlations

library(Hmisc)

# linear
rcorr(data_across$list_score, data_across$eduflow , type="pearson") 
rcorr(data_across$list_class, data_across$eduflow , type="pearson") 

# non linear
rcorr(data_across$list_score, data_across$eduflow , type="spearman") 
rcorr(data_across$list_class, data_across$eduflow , type="spearman") 

# best: pearson, class/eduflow

rcorr(data_across$list_class, data_across$eduflow , type="pearson") 
plot(data_across$list_class, data_across$eduflow)
abline(lm(data_across$eduflow ~ data_across$list_class))

linear_regres = lm(data_across$eduflow ~ data_across$list_class)
linear_coeff = coefficients(linear_regres)
summary(linear_coeff)
fitted(linear_regres)
abline(4.871517,1.628709)

# equation
# y = 1.628709 * x + 4.871517

x = (7 - 4.871517) / 1.628709

## left / right

data_split = data_mean_bis
data_split$class_left = data_split$list_class
data_split$class_right = data_split$list_class
data_split[data_split$list_direction == 0,]$class_right = data_split[data_split$list_direction == 1,]$class_right
data_split = data_split[data_split$list_direction == 0,]
data_split$class_both = data_split$class_left + data_split$class_right

lm(data_split$eduflow ~ data_split$class_left + data_split$class_right)

lm(data_split$eduflow ~ data_split$class_both)

# dist max is sqrt(8)
data_split$dist = sqrt(8) - sqrt((1 - data_split$class_left)^2 + (1 - data_split$class_right)^2 )


plot(data_split$dist, data_split$eduflow)

rcorr(data_split$eduflow,data_split$dist, type="pearson")
lm(data_split$eduflow ~ data_split$dist )
abline(3.271, 1.211)

# y = 1.211 * x + 4.274

x = (7 - 3.271) / 1.211

#3D version

##


data_left = data_mean_bis[data_mean_bis$list_direction == 0,]
plot(data_left$list_score, data_left$eduflow)
plot(data_left$list_class, data_left$eduflow)
lm(data_left$eduflow ~ data_left$list_class)

data_right = data_mean_bis[data_mean_bis$list_direction == 1,]
plot(data_right$list_score, data_right$eduflow)
plot(data_right$list_class, data_right$eduflow)
lm(data_right$eduflow ~ data_right$list_class)


plot(data_across$list_score, data_across$eduflow)

