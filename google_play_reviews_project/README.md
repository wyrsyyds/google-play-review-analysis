# Google Play Review Analysis – Exploratory Analysis & Data Quality Assessment

## Overview
This repository contains an exploratory and descriptive analysis of Google Play Store reviews for a high-activity application. The goal of this work is to assess the quality and structure of the raw review data, identify key behavioral and temporal patterns, and understand potential biases before any downstream labeling or modeling.

The analysis focuses on understanding whether the dataset is suitable for further analytical use, rather than building models at this stage.

---

## Data Collection
Reviews were collected from the Google Play Store using multiple sorting regimes:
- **Newest**
- **Most relevant**

Collecting across multiple sort orders was done intentionally to reduce reliance on a single platform-defined view and to mitigate pure recency or engagement bias. The resulting dataset contains approximately **15,873 reviews** spanning a range of time periods and engagement profiles.

---

## Exploratory Analysis
The exploratory analysis examines several key dimensions of the data:

### Rating Distribution
- Ratings are highly polarized, with a strong concentration at 5-star and a meaningful share of 1-star reviews.
- Neutral ratings (2–4 stars) are relatively underrepresented, indicating self-selection effects in review behavior.

### Temporal Patterns
- Review volume exhibits a strong recency skew, with most reviews concentrated in recent months.
- Average ratings vary meaningfully over time, suggesting non-stationary sentiment dynamics that may reflect product updates or changes in user experience.

### Rating Behavior & Engagement
- Lower-rated reviews tend to be longer and more detailed, while higher-rated reviews are often short and affirmational.
- Engagement (thumbs-up) varies by rating and appears to reward perceived informativeness rather than rating extremity alone.

### Text Characteristics
- Review text length is highly right-skewed, with many short reviews and a long tail of more detailed feedback.
- Short, low-effort reviews are disproportionately concentrated among 5-star ratings.

---

## Data Quality Assessment
The raw dataset was evaluated for readiness and consistency:

- **Missing values:** Core fields such as rating, review date, and review text are well-populated, while some metadata fields exhibit partial missingness.
- **Duplicates:** Duplicate reviews are minimal, indicating low redundancy in the collected data.
- **Formatting & consistency:** Key fields have consistent data types and expected value ranges.
- **Preprocessing considerations:** Prior to labeling or modeling, steps such as handling empty text, normalizing timestamps, filtering very short reviews, and bias-aware sampling would be required.

---

## Biases & Limitations
Several structural biases are present in the data:
- Strong polarization toward extreme ratings (1 and 5 stars)
- Recency bias driven by platform loading behavior and app adoption dynamics
- Sorting-mode bias, where “newest” and “most relevant” views yield different rating mixes

These biases are intrinsic to the platform and user behavior and should be addressed analytically rather than through additional data collection alone.

---

## Repository Structure
