
swedish_data = read.csv("swedish_stats.csv")  # read csv file 
swedish_data$score = as.numeric(sub(",", ".", swedish_data$score, fixed = TRUE))

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
perf_data$swedish = -1

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
  
  # swedish_data
  swedish_score = swedish_data[swedish_data$ID == id,]$score
  cat("swedish score", swedish_score, "\n")
  perf_data[perf_data$list_id == id,]$swedish = swedish_score
  
  
}


data_mean = aggregate( cbind(list_class, list_score, eduflow, eduflow3D, swedish) ~ list_id + list_cond + list_direction, data = perf_data, FUN = mean)
 
# how score and classifier output relate
plot(data_mean$list_class, data_mean$list_score)

# reverse left classifier output
data_mean_bis = data_mean
data_mean_bis[data_mean_bis$list_direction == 0,]$list_class = data_mean_bis[data_mean_bis$list_direction == 0,]$list_class * -1

# score/classifier, no matter class
plot(data_mean_bis$list_class, data_mean_bis$list_score)

# average across left/right
data_across = aggregate( cbind(list_class, list_score, eduflow, eduflow3D, swedish) ~ list_id + list_cond, data = data_mean_bis, FUN = mean)

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
plot(data_split$dist, data_split$eduflow3D)

rcorr(data_split$eduflow3D,data_split$dist, type="pearson")
lm(data_split$eduflow3D ~ data_split$dist )
abline(3.318, 1.265)
x = (7 - 3.318) / 1.265

## trying to account for flow

data_split$swedish7 = ((data_split$swedish - 1) / 5 * 7 )+ 1
data_split$dist_flow = data_split$eduflow3D - data_split$swedish7

plot(data_split$dist, data_split$dist_flow)
rcorr(data_split$dist_flow,data_split$dist, type="pearson")
model = lm( data_split$dist ~ data_split$eduflow3D + data_split$swedish7)

summary(model)
abline(model)


# test with average

data_split$dist_flow2 = data_split$eduflow3D - (data_split$swedish7 - mean(data_split$swedish7 ))

plot(data_split$dist, data_split$dist_flow2)
rcorr(data_split$dist_flow2,data_split$dist, type="pearson")
model = lm(data_split$dist_flow2 ~ data_split$dist)
summary(model)
x = (7 - 3.083) / 1.422
# target
sqrt((x*x)/2) - 1

# test with (pseudo?) z-score

data_split$dist_flow2 = data_split$eduflow3D -  scale(data_split$swedish7 )

plot(data_split$dist, data_split$dist_flow2)
rcorr(data_split$dist_flow2,data_split$dist, type="pearson")
model = lm(data_split$dist_flow2 ~ data_split$dist)
summary(model)

x = (7 - 2.618) / 1.731
# target
sqrt((x*x)/2) - 1

