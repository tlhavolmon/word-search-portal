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
    {"q": "An output used to test association between variables.", "a": "CHISQUARE"},
    {"q": "Lists variables that are used for an analysis in SAS when computing the frequencies.", "a": "TABLES"},
    {"q": "A # is used when making comments using this programming language.", "a": "PYTHON"},
    {"q": "An option used to print the sorted dataset to a SAS output file.", "a": "OUT"},
    {"q": "Computes normality tests in SAS.", "a": "PROCUNIVARIATE"},
    {"q": "A procedure used to compute skewness and kurtosis in SAS.", "a": "MEANS"},
    {"q": "A graphical test for bivariate relationship testing.", "a": "SCATTERPLOT"},
    {"q": "We interpret this when we want to determine significance of any test regardless of the software used to generate the output.", "a": "PVALUE"},
    {"q": "Used to output basic descriptive statistics for a continuous variable and for outputting regression model outputs in the R software.", "a": "SUMMARY"},
    {"q": "The < - is used when creating this in the R software.", "a": "FUNCTIONS"},
    {"q": "A procedure that does not produce an output in SAS unless the print procedure is used after it.", "a": "SORT"},
    {"q": "A coefficient used to test the strength and direction of a significant relationship.", "a": "CORRELATION"},
    {"q": "Used to display 45 degree line on a QQ plot in R.", "a": "QQLINE"},
    {"q": "If this test is not significant, there is no need to interpret the parameter estimates for the model and the R-square.", "a": "ANOVA"},
    {"q": "Used to preview the data in R and python.", "a": "HEAD"}
]

WORDS_TO_FIND = [item["a"] for item in ASSESSMENT_DATA]
GRID_SIZE = 18

def generate_word_search_grid():
    grid = [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    # Allowed directions: horizontal right, vertical down, diagonal down-right
    allowed_directions = [(0, 1), (1, 0), (1, 1)]
    
    word_placements = {}
    for word in WORDS_TO_FIND:
        placed = False
        attempts = 0
        while not placed and attempts < 500:
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
            
    # Fill remaining empty cells completely with random letters (no more 'X's)
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
if 'found_words' not in st.session_state:
    st.session_state.found_words = set()
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

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

# ----------------- APP RENDERING ROUTING -----------------

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
        g, p = generate_word_search_grid()
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

elif st.session_state.authenticated and not st.session_state.is_admin:
    elapsed = int(time.time() - st.session_state.start_time)
    rem_time = max(0, (30 * 60) - elapsed)
    if rem_time <= 0:
        save_assessment_record(st.session_state.user_id, len(st.session_state.found_words)*2, st.session_state.start_time)
        st.session_state.authenticated = False
        st.error("Time Expired! Your assessment has been auto-submitted.")
        time.sleep(2)
        st.rerun()
        
    mins, secs = divmod(rem_time, 60)
    col1, col2, col3 = st.columns(3)
    col1.subheader(f"Candidate: {st.session_state.user_id}")
    col2.metric("Time Remaining", f"{mins:02d}:{secs:02d}")
    current_score = len(st.session_state.found_words) * 2
    col3.metric("Score", f"{current_score} Marks")
    
    st.markdown("---")
    left_layout, right_layout = st.columns(2)
    
    with left_layout:
        st.markdown("#### Word Search Puzzle Matrix")
        st.caption("Correctly verified words automatically highlight in green below 👇")
        
        highlighted_coords = set()
        for fw in st.session_state.found_words:
            if fw in st.session_state.placements:
                for coord in st.session_state.placements[fw]:
                    highlighted_coords.add(coord)
        
        grid_html = "<div style='display: grid; grid-template-columns: repeat(18, 1fr); gap: 2px; font-family: monospace; font-weight: bold; font-size:0.85rem; text-align:center;'>"
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                letter = st.session_state.grid[r][c]
                if (r, c) in highlighted_coords:
                    grid_html += f"<div style='background-color:#2ecc71; color:white; padding:4px 0; border-radius:2px;'>{letter}</div>"
                else:
                    grid_html += f"<div style='background-color:#f8f9fa; color:#2c3e50; padding:4px 0; border:1px solid #dee2e6; border-radius:2px;'>{letter}</div>"
        grid_html += "</div>"
        st.markdown(grid_html, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        guess = st.text_input("Type discovered term sequences in UPPERCASE:", key="word_guess", value="").strip().upper()
        if st.button("Verify Found Word", use_container_width=True):
            if guess in WORDS_TO_FIND and guess not in st.session_state.found_words:
                st.session_state.found_words.add(guess)
                st.success(f"Correct Sequence Authenticated: +2 Marks ({guess})")
                time.sleep(0.5)
                st.rerun()
            elif guess in st.session_state.found_words:
                st.warning("Sequence has already been verified previously.")
            else:
                st.error("Invalid sequence pattern entry matched.")
                
    with right_layout:
        st.markdown("#### Assessment Questions (2 Marks Each)")
        for idx, item in enumerate(ASSESSMENT_DATA, 1):
            is_done = item["a"] in st.session_state.found_words
            if is_done:
                st.markdown(f"~~{idx}. {item['q']}~~ 🟢 **[SOLVED]**")
            else:
                st.markdown(f"*{idx}.* {item['q']}")
        st.markdown("---")
        if st.button("Finalize and Submit Examination Paper", type="primary", use_container_width=True):
            save_assessment_record(st.session_state.user_id, current_score, st.session_state.start_time)
            st.success(f"Submission recorded! Final Mark assigned: {current_score} Marks.")
            time.sleep(2)
            st.session_state.authenticated = False
            st.rerun()

else:
    st.title("Portal Authentication Gate")
    user_code = st.text_input("Enter Student Number / Admin Staff Number:", value="", autocomplete="off")
    if st.button("Authenticate & Access", use_container_width=True):
        user_code = user_code.strip()
        if user_code == ADMIN_STAFF_NUMBER:
            st.session_state.authenticated = True
            st.session_state.user_id = user_code
            st.session_state.is_admin = True
            st.rerun()
        elif user_code in AUTHORIZED_STUDENTS:
            db = SessionLocal()
            existing = db.query(AssessmentResult).filter(AssessmentResult.student_number == user_code).first()
            db.close()
            if existing:
                st.error("Authentication failed. This student record has already logged a grading attempt.")
            else:
                st.session_state.authenticated = True
                st.session_state.user_id = user_code
                st.session_state.is_admin = False
                g, p = generate_word_search_grid()
                st.session_state.grid = g
                st.session_state.placements = p
                st.session_state.found_words = set()
                st.session_state.start_time = time.time()
                st.rerun()
        else:
            st.error("The code entered is not registered on the system.")

    st.markdown("---")
    with st.expander("🛠️ Admin Identity Override System"):
        staff_code = st.text_input("Enter Staff Code:", type="password", key="override_staff")
        alt_id = st.text_input("Create Alternate Student Identity String:", key="override_alt")
        if st.button("Force Establish Session"):
            if staff_code.strip() == ADMIN_STAFF_NUMBER and alt_id.strip():
                st.session_state.authenticated = True
                st.session_state.user_id = alt_id.strip()
                st.session_state.is_admin = False
                g, p = generate_word_search_grid()
                st.session_state.grid = g
                st.session_state.placements = p
                st.session_state.found_words = set()
                st.session_state.start_time = time.time()
                st.rerun()
            else:
                st.error("Invalid credentials or fields missing.")
