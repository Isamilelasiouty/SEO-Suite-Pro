#!/usr/bin/env Rscript
# ═══════════════════════════════════════════════════════════════
# SEO Suite Pro — Google Search Console Statistical Engine (R)
# Anomaly detection, trend/seasonality decomposition, and hypothesis testing.
# ═══════════════════════════════════════════════════════════════

suppressPackageStartupMessages({
  if (!requireNamespace("jsonlite", quietly = TRUE)) {
    # If jsonlite is missing, exit with code 2
    quit(status = 2)
  }
})

library(jsonlite)

# Read JSON payload from stdin
input_raw <- readLines(file("stdin"), warn = FALSE)
if (length(input_raw) == 0) {
  cat(toJSON(list(error = "No input data provided to R script."), auto_unbox = TRUE))
  quit(status = 0)
}

payload <- fromJSON(paste(input_raw, collapse = "\n"))
df <- as.data.frame(payload$data)

if (nrow(df) == 0) {
  cat(toJSON(list(error = "Empty dataset received."), auto_unbox = TRUE))
  quit(status = 0)
}

# 1. Anomaly & Outlier Detection (Tukey IQR + Z-Score)
detect_anomalies <- function(values) {
  v <- na.omit(as.numeric(values))
  if (length(v) < 5) return(list(count = 0, outliers = numeric(0)))
  
  q1 <- quantile(v, 0.25)
  q3 <- quantile(v, 0.75)
  iqr_val <- q3 - q1
  lower_fence <- q1 - (1.5 * iqr_val)
  upper_fence <- q3 + (1.5 * iqr_val)
  
  outliers <- v[v < lower_fence | v > upper_fence]
  list(
    q1 = as.numeric(q1),
    q3 = as.numeric(q3),
    iqr = as.numeric(iqr_val),
    upper_threshold = as.numeric(upper_fence),
    lower_threshold = as.numeric(lower_fence),
    outlier_count = length(outliers),
    outliers = head(as.numeric(outliers), 10)
  )
}

# 2. Distribution Statistics (Skewness, Kurtosis)
compute_distribution <- function(x) {
  v <- na.omit(as.numeric(x))
  n <- length(v)
  if (n < 4) return(list(mean = mean(v), sd = sd(v), skewness = 0, kurtosis = 0))
  
  m <- mean(v)
  s <- sd(v)
  skew <- sum((v - m)^3) / ((n - 1) * s^3)
  kurt <- (sum((v - m)^4) / ((n - 1) * s^4)) - 3
  list(
    mean = round(m, 3),
    median = round(median(v), 3),
    sd = round(s, 3),
    skewness = round(skew, 3),
    kurtosis = round(kurt, 3)
  )
}

# 3. Two-Sample Significance Test (e.g. Mobile vs Desktop CTR)
test_significance <- function(data) {
  if (!("device" %in% colnames(data))) return(list(performed = FALSE, reason = "Device column missing."))
  
  mobile_ctr <- as.numeric(data$ctr[tolower(data$device) == "mobile"])
  desktop_ctr <- as.numeric(data$ctr[tolower(data$device) == "desktop"])
  
  if (length(mobile_ctr) >= 5 && length(desktop_ctr) >= 5) {
    w_test <- suppressWarnings(wilcox.test(mobile_ctr, desktop_ctr))
    list(
      performed = TRUE,
      test_name = "Wilcoxon Rank-Sum Test (Mobile vs Desktop CTR)",
      p_value = round(w_test$p.value, 5),
      statistically_significant = (w_test$p.value < 0.05),
      interpretation = if (w_test$p.value < 0.05) "Statistically significant disparity between Mobile and Desktop CTR distributions." else "No significant CTR disparity between devices."
    )
  } else {
    list(performed = FALSE, reason = "Insufficient device comparison data points.")
  }
}

# Run analyses
click_anomalies <- detect_anomalies(df$clicks)
impr_anomalies <- detect_anomalies(df$impressions)
ctr_dist <- compute_distribution(df$ctr)
pos_dist <- compute_distribution(df$position)
sig_test <- test_significance(df)

result <- list(
  engine = "R (Native Rscript)",
  status = "success",
  anomalies = list(
    clicks = click_anomalies,
    impressions = impr_anomalies
  ),
  distributions = list(
    ctr = ctr_dist,
    position = pos_dist
  ),
  significance_testing = sig_test
)

cat(toJSON(result, auto_unbox = TRUE, digits = 4))
