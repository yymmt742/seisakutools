library(colourvision)

# 犬の錐体 λmax (nm)
lambda_max <- c(429, 555)

# 300–700 nm, 1 nm刻み
spec <- photor(
    lambda.max = c(429, 555),
    lambda = seq(300, 700, 1),
    beta.band = TRUE   # Govardovskii完全版
)

str(spec)
head(spec)

# 中身を確認
head(spec)

write.csv(
    spec,
    file = "dog_cones.csv",
    row.names = FALSE
)
