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
    "30996724", "53269713", "47904844", "40801942", "55952453", "53351878", "38848058", "49539817", 
    "52502058", "47043709", "34331646", "37182927", "55246109", "47943203", "55950027", "54790352", 
    "56161786", "52028356", "37988530", "45706719", "42926289", "4612054", "39313913", "46833684", 
    "43463827", "38746239", "45430373", "45389764", "45670080", "51473925", "51633515", "53974123", 
    "32500890", "54589363", "55849873", "46528504", "52207048", "46490078", "42702798", "55864937", 
    "45214115", "52246183"
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
    """Generates a randomized word search grid where words ONLY read forward."""
    grid = [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    allowed_directions = [(0, 1), (1, 0), (1, 1)]
    word_placements = {}
    
    for word in words_list:
        placed = False
        attempts = 0
        while not placed and attempts < 600:
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
                    coords = []
                    for i in range(len(word)):
                        curr_r = r + d[0] * i
                        curr_c = c + d[1] * i
                        grid[curr_r][curr_c] = word[i]
                        coords.append((curr_r, curr_c))
                    word_placements[word] = coords
                    placed = True
            attempts += 1
            
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == ' ':
                grid[r][c] = random.choice(string.ascii_uppercase)
    return grid, word_placements

# Initialize App Session Memory
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'grid' not in st.session_state:
    st.session_state.grid = None
if 'placements' not in st.session_state:
    st.session_state.placements = {}
if 'shuffled_assessment' not in st.session_state:
    st.session_state.shuffled_assessment = []
if 'found_words' not in st.session_state:
    st.session_state.found_words = set()
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'completed_submitted' not in st.session_state:
    st.session_state.completed_submitted = False
if 'show_quit_warning' not in st.session_state:
    st.session_state.show_quit_warning = False

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

# ----------------- APP ROUTING CONTROLLER -----------------
if st.session_state.authenticated and st.session_state.is_admin:
    st.sidebar.title("Admin Console")
    if st.sidebar.button("Sign Out"):
        st.session_state.authenticated = False
        st.session_state.is_admin = False
        st.rerun()
        
    st.title("Administrative Grade Console")
    if st.button("🚀 Run Application Test (Practice Mode)", use_container_width=True):
        st.session_state.user_id = "ADMIN-TEST"
        st.session_state.is_admin = False
        st.session_state.completed_submitted = False
        shuffled = list(ASSESSMENT_DATA)
        random.shuffle(shuffled)
        st.session_state.shuffled_assessment = shuffled
        words_list = [item["a"] for item in shuffled]
        g, p = generate_word_search_grid(words_list)
        st.session_state.grid = g
        st.session_state.placements = p
        st.session_state.found_words = set()
        st.session_state.start_time = time.time()
        st.session_state.show_quit_warning = False
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

elif st.session_state.authenticated and not st.session_state.is_admin:
    all_possible_words = [item["a"] for item in st.session_state.shuffled_assessment]
    current_score = len(st.session_state.found_words) * 2
    
    # Check if 30-minute time limit has elapsed
    elapsed = int(time.time() - st.session_state.start_time)
    rem_time = max(0, (30 * 60) - elapsed)
    
    if rem_time <= 0 and not st.session_state.completed_submitted:
        st.session_state.completed_submitted = True
        save_assessment_record(st.session_state.user_id, current_score, st.session_state.start_time)
        st.error("⏰ Time Expired! Your assessment has been automatically submitted.")
        time.sleep(3)
        st.session_state.authenticated = False
        st.session_state.completed_submitted = False
        st.rerun()
        
    # Check if student completed all questions successfully
    if len(st.session_state.found_words) == len(all_possible_words) and not st.session_state.completed_submitted:
        st.session_state.completed_submitted = True
        save_assessment_record(st.session_state.user_id, current_score, st.session_state.start_time)
        
    if st.session_state.completed_submitted:
        st.balloons()
        st.success("🎉 Outstanding! You have successfully completed all questions correctly.")
