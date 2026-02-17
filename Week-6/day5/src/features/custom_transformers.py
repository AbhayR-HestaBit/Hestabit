from sklearn.base import BaseEstimator, TransformerMixin

# generates new features for modeling
class CustomFeatureGenerator(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    # adds derived features to dataframe
    def transform(self, X):
        X = X.copy()

        if "cgpa" in X.columns and "aptitude_skill_rating" in X.columns:
            X["academic_strength"] = X["cgpa"] * X["aptitude_skill_rating"]

        if "study_hours_per_day" in X.columns and "attendance_percentage" in X.columns:
            X["discipline_score"] = X["study_hours_per_day"] * X["attendance_percentage"]

        if "certifications_count" in X.columns and "projects_completed" in X.columns:
            X["profile_strength"] = X["certifications_count"] + X["projects_completed"]

        if all(col in X.columns for col in ["coding_skill_rating", "communication_skill_rating", "aptitude_skill_rating"]):
            X["total_skills"] = X["coding_skill_rating"] + X["communication_skill_rating"] + X["aptitude_skill_rating"]

        if "tenth_percentage" in X.columns and "twelfth_percentage" in X.columns:
            X["school_avg"] = (X["tenth_percentage"] + X["twelfth_percentage"]) / 2

        if "cgpa" in X.columns:
            X["cgpa_percentage"] = X["cgpa"] * 9.5

        if all(col in X.columns for col in ["internships_completed", "projects_completed", "hackathons_participated"]):
            X["achievement_score"] = (X["internships_completed"] * 2) + X["projects_completed"] + X["hackathons_participated"]

        if "cgpa" in X.columns and "study_hours_per_day" in X.columns:
            X["efficiency_score"] = X["cgpa"] / (X["study_hours_per_day"] + 1)

        if "stress_level" in X.columns and "sleep_hours" in X.columns:
            X["stress_to_sleep_ratio"] = X["stress_level"] / (X["sleep_hours"] + 1)
            
        if "total_skills" in X.columns and "achievement_score" in X.columns:
             X["overall_rating"] = (X["total_skills"] + X["achievement_score"]) / 2
             
        if "certifications_count" in X.columns and "projects_completed" in X.columns and "profile_strength" not in X.columns:
             X["profile_strength"] = X["certifications_count"] + X["projects_completed"]

        return X

    def fit_transform(self, X, y=None):
        return self.fit(X, y).transform(X)
