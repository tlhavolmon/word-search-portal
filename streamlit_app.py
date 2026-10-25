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
    "37988530", "45706719", "42926289", "4612054",  "39313913", "46833684", 
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
    {"q": "An output used to test association between variables.", "a": "CHISQAURE"},
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

WORDS_TO_FIND = [item["a"] for item in ASSESSMENT_DATA]
GRID_SIZE = 18

def generate_word_search_grid_with_mapping():
    grid = [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    word_placements = {}
    allowed_directions = [(-1, 1), (0, 1), (1, 0)]
    
    for word in WORDS_TO_FIND:
        placed = False
        attempts = 0
        while not placed and attempts < 250:
            d = random.choice(allowed_directions)
            r = random.randint(0, GRID_SIZE - 1)
            c = random.randint(0, GRID_SIZE - 1)
            end_r = r + d[0] * (len(word) - 1)
            end_c = c + d[1] * (len(word) - 1)
            if 0 <= end_r < GRID_SIZE and 0 <= end_c < GRID_SIZE:
                can_place = True
                for i in range(len(word)):
                    nr, nc = r + d[0] * i, c + d[1] * i
                    if grid[nr][nc] != ' ' and grid[nr][nc] != word[i]:
                        can_place = False
                        break
                if can_place:
                    word_placements[word] = []
                    for i in range(len(word)):
                        nr, nc = r + d[0] * i, c + d[1] * i
                        grid[nr][nc] = word[i]
                        word_placements[word].append((nr, nc))
                    placed = True
            attempts += 1
            
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == ' ':
                grid[r][c] = random.choice(string.ascii_uppercase)
                
    return grid, word_placements

# Setup memory tracking structures
session_defaults = {
    'authenticated': False,
    'user_id': None,
    'is_admin': False,
    'grid': None,
    'placements': {},
    'found_words': set(),
    'start_time': None
}
for key, value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

def save_assessment_record(student_id, final_score, start_epoch):
    elapsed_seconds = int(time.time() - start_epoch)
    mins, secs = divmod(elapsed_seconds, 60)
    duration_str = f"{mins}m {secs}s"
    
    if student_id != "ADMIN-TEST":
        db = SessionLocal()
        try:
            existing = db.query(AssessmentResult).filter(AssessmentResult.student_number == student_id).first()
            if not existing:
                record = AssessmentResult(student_number=student_id, score=final_score, duration=duration_str)
                db.add(record)
                db.commit()
        except Exception as e:
            st.error(f"Database error: {e}")
        finally:
            db.close()

# ----------------- ROUTING VIEW SYSTEMS -----------------

if st.session_state.get('authenticated') and st.session_state.get('is_admin'):
    st.sidebar.title("Admin Console")
    if st.sidebar.button("Sign Out"):
        st.session_state.authenticated = False
        st.session_state.is_admin = False
        st.rerun()
        
    st.title("Administrative Grade Console")
    if st.button("🚀 Run Application Test (Practice Mode)"):
        st.session_state.user_id = "ADMIN-TEST"
        st.session_state.is_admin = False
        g, p = generate_word_search_grid_with_mapping()
        st.session_state.grid = g
        st.session_state.placements = p
        st.session_state.found_words = set()
        st.session_state.start_time = time.time()
        st.rerun()
        
    st.markdown("### Student Grading Ledger")
    db = SessionLocal()
    records = db.query(AssessmentResult).all()
    db.close()
    
    if records:
        table_data = [{
            "Student Number": r.student_number, 
            "Final Mark": f"{r.score} Marks", 
            "Duration": r.duration, 
            "Submission Timestamp": r.submission_time.strftime('%Y-%m-%d %H:%M:%S')
        } for r in records]
        st.table(table_data)
    else:
        st.info("No student records have been logged in the tracking database yet.")

elif st.session_state.get('authenticated') and not st.session_state.get('is_admin'):
    elapsed = int(time.time() - st.session_state.get('start_time', time.time()))
    rem_time = max(0, (30 * 60) - elapsed)
    
    if rem_time <= 0:
        save_assessment_record(st.session_state.user_id, len(st.session_state.get('found_words', set()))*2, st.session_state.start_time)
        st.session_state.authenticated = False
        st.error("Time Expired! Your assessment has been auto-submitted.")
        time.sleep(2)
        st.rerun()

    mins, secs = divmod(rem_time, 60)
    col1, col2, col3 = st.columns(3)
    col1.subheader(f"Candidate Session: {st.session_state.get('user_id')}")
    col2.metric("Time Remaining", f"{mins:02d}:{secs:02d}")
    current_score = len(st.session_state.get('found_words', set())) * 2
    col3.metric("Score", f"{current_score} Marks")
    
    st.markdown("---")
    left_layout, right_layout = st.columns(2)
    
    with left_layout:
        st.markdown("#### Word Search Puzzle Matrix")
        
        highlighted_coordinates = set()
        active_placements = st.session_state.get('placements', {}) or {}
        for verified_word in st.session_state.get('found_words', set()):
            if verified_word in active_placements:
                for coord in active_placements[verified_word]:
                    highlighted_coordinates.add(coord)
                    
        current_grid = st.session_state.get('grid', [])
        grid_html = "<div style='display: grid; grid-template-columns: repeat(18, 1fr); gap: 2px; font-family: monospace; font-weight: bold; font-size:1rem; text-align:center;'>"
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if r < len(current_grid) and c < len(current_grid[r]):
                    letter = current_grid[r][c]
                else:
                    letter = " "
                
                if (r, c) in highlighted_coordinates:
                    grid_html += f"<div style='background-color:#2ecc71; padding:2px; border:1px solid #27ae60; color:white;'>{letter}</div>"
                else:
