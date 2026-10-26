import random
import string
import time
import os
from datetime import datetime
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# Optimized cloud-compatible dynamic directory paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'assessment_portal.db')}"

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class AssessmentResult(Base):
    __tablename__ = "assessment_results"
    id = Column(Integer, primary_key=True, index=True)
    student_number = Column(String, unique=True, nullable=False)
    score = Column(Integer, nullable=False)
    duration = Column(String, nullable=False)
    submission_time = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

ADMIN_STAFF_NUMBER = "22297812"
AUTHORIZED_STUDENTS = {
    "30996724", "53269713", "47904844", "40801942", "55952453", "53351878",
    "38848058", "49539817", "52502058", "47043709", "34331646", "37182927",
    "55246109", "47943203", "55950027", "54790352", "56161786", "52028356",
    "37988530", "45706719", "42926289", "4612054", "39313913", "46833684",
    "43463827", "38746239", "45430373", "45389764", "45670080", "51473925",
    "51633515", "53974123", "32500890", "54589363", "55849873", "46528504",
    "52207048", "46490078", "42702798", "55864937", "45214115", "52246183"
}

ASSESSMENT_DATA = [
    {"q": "Student number, Name of the Province and Identity Number are defined as this type of variable in SPSS variable view.", "a": "STRING"},
    {"q": "/* */ are used for this purpose.", "a": "COMMENTING"},
    {"q": "Used for selecting variables in an R script.", "a": "DOLLARSIGN"},
    {"q": "Can be used interchangeably with cards.", "a": "DATALINES"},
    {"q": "There is no need to define the data set name and capture it directly into SAS after doing this with any data from SPSS, SAS, R or Stata.", "a": "IMPORTING"},
    {"q": "Prints out every step that is executed in SAS.", "a": "LOGWINDOW"},
    {"q": "An output used to test association between variables.", "a": "CHISQUARE"},
    {"q": "Lists variables that are used for an analysis in SAS when computing the frequencies.", "a": "TABLES"},
    {"q": "A # is used when making comments using this programming language.", "a": "PYTHON"},
    {"q": "An option used to print the sorted dataset to a SAS output file.", "a": "OUT"},
    {"q": "Computes normality tests in SAS.", "a": "PROCUNIVARIATE"},
    {"q": "A procedure used to compute skewness and kurtosis in SAS.", "a": "MEANS"},
    {"q": "A graphical test for bivariate relationship testing.", "a": "SCATTERPLOT"},
    {"q": "We interpret this when we want to determine significance of any test regardless of the software used to generate the output.", "a": "PVALUE"},
    {"q": "Used to output basic descriptive statistics for a continuous variable and for outputting regression model outputs in the R software.", "a": "SUMMARY"},
    {"q": "The <- is used when creating this in the R software.", "a": "FUNCTIONS"},
    {"q": "A procedure that does not produce an output in SAS unless the print procedure is used after it.", "a": "SORT"},
    {"q": "A coefficient used to test the strength and direction of a significant relationship.", "a": "CORRELATION"},
    {"q": "Used to display 45 degree line on a QQ plot in R.", "a": "QQLINE"},
    {"q": "If this test is not significant, there is no need to interpret the parameter estimates for the model and the R-square.", "a": "ANOVA"},
    {"q": "Used to preview the data in R and python.", "a": "HEAD"}
]

GRID_SIZE = 18

def generate_word_search_grid(words_list):
    """Generates a randomized word search grid where words ONLY read forward (Right, Down, Diagonal-Down-Right)."""
    grid = [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    allowed_directions = [(0, 1), (1, 0), (1, 1)]
    
    word_placements = {}
    for word in words_list:
        placed = False
        attempts =
