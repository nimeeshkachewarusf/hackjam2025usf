import time
import os
import re
from playwright.sync_api import sync_playwright

# --- 1. CONFIGURATION ---
# NOTE: Update this path to where you saved your DUMMY.HTML file!


# Construct the full, absolute path to the HTML file located next to the executable
# --- 1. CONFIGURATION ---
# NOTE: The batch script will ensure this path is relative to the script's location.
DUMMY_REGISTRATION_URL = "file:///C:/COP%20Project%20Files/DUMMY.HTML"

# ... (rest of your Python code) ...

# Map for day abbreviations to numerical keys (Mon=1 to Fri=5)
DAY_MAP = {"M": 1, "Tu": 2, "W": 3, "Th": 4, "F": 5}
# Map day keys to HTML IDs for injection (NEW)
DAY_ID_MAP = {
    1: "mon-events", 
    2: "tue-events", 
    3: "wed-events", 
    4: "thu-events", 
    5: "fri-events"
}


# --- 2. THE AI'S KNOWLEDGE BASE (Historical Grades) ---
HISTORICAL_GRADES = {
    "Zhang, X.": 3.2, "Yi, H.": 2.5, "Liu, F.": 3.5, 
    "Pamplona Segundo, V.": 3.8, "Zhang, Y.": 3.1, "Karthik, R.": 3.2, "Smith, A.": 2.9, 
    "Fang, S.": 3.7, "Anderson, J.": 2.8, 
    "Woods, J.": 3.3, "Voronin, D.": 3.9, 
    "Wang, J.": 3.6, "Gaspar, A.": 3.1, 
    "Linatti, L.": 3.0, "Qui, X.": 2.2, 
    "Korzhova, V.": 2.9, "Kaleemurisa, E.": 3.5, 
    "Martinez, C.": 3.4, "Johnson, R.": 3.0
}

# --- 3. DUMMY COURSE OFFERINGS ---
COURSE_OFFERINGS = {
    "COP 4600": {
        "title": "Operating Systems",
        "sections": [
            {"crn": "14808", "section": "001", "days": "TuTh", "time": "08:00 AM - 09:15 AM", "instructor": "Pamplona Segundo, V.", "status": "Open", "enrolled": 25, "capacity": 40},
            {"crn": "14809", "section": "002", "days": "TuTh", "time": "09:30 AM - 10:45 AM", "instructor": "Zhang, Y.", "status": "FULL", "enrolled": 40, "capacity": 40},
            {"crn": "14810", "section": "003", "days": "MW", "time": "09:30 AM - 10:45 AM", "instructor": "Karthik, R.", "status": "Open", "enrolled": 30, "capacity": 40},
            {"crn": "14811", "section": "004", "days": "MW", "time": "02:00 PM - 03:15 PM", "instructor": "Smith, A.", "status": "Open", "enrolled": 20, "capacity": 40}
        ]
    },
    "CDA 3103": {
        "title": "Computer Organization",
        "sections": [
            {"crn": "14080", "section": "001", "days": "TuTh", "time": "02:00 PM - 03:15 PM", "instructor": "Zhang, X.", "status": "Open", "enrolled": 35, "capacity": 40},
            {"crn": "14087", "section": "002", "days": "TuTh", "time": "08:00 AM - 09:15 AM", "instructor": "Yi, H.", "status": "Open", "enrolled": 25, "capacity": 40},
            {"crn": "14088", "section": "003", "days": "MW", "time": "12:30 PM - 01:45 PM", "instructor": "Liu, F.", "status": "Open", "enrolled": 28, "capacity": 40}
        ]
    },
    "CEN 4020": {
        "title": "Software Engineering",
        "sections": [
            {"crn": "14913", "section": "001", "days": "TuTh", "time": "03:30 PM - 04:45 PM", "instructor": "Fang, S.", "status": "Open", "enrolled": 30, "capacity": 40},
            {"crn": "14914", "section": "002", "days": "MW", "time": "06:00 PM - 07:15 PM", "instructor": "Anderson, J.", "status": "FULL", "enrolled": 40, "capacity": 40}
        ]
    },
    "PHY 2048": {
        "title": "General Physics I with Calculus",
        "sections": [
            {"crn": "10328", "section": "001", "days": "Online", "time": "Asynchronous", "instructor": "Woods, J.", "status": "FULL", "enrolled": 40, "capacity": 40},
            {"crn": "10345", "section": "005", "days": "TuTh", "time": "06:00 PM - 07:15 PM", "instructor": "Voronin, D.", "status": "Open", "enrolled": 22, "capacity": 40}
        ]
    },
    "COP 3514": {
        "title": "Program Design",
        "sections": [
            {"crn": "14879", "section": "001", "days": "MW", "time": "11:00 AM - 12:15 PM", "instructor": "Wang, J.", "status": "FULL", "enrolled": 40, "capacity": 40},
            {"crn": "14887", "section": "002", "days": "MW", "time": "06:30 PM - 07:45 PM", "instructor": "Gaspar, A.", "status": "Open", "enrolled": 15, "capacity": 40}
        ]
    },
    "CNT 4419": {
        "title": "Secure Coding Techniques",
        "sections": [
            {"crn": "14910", "section": "001", "days": "TuTh", "time": "03:30 PM - 04:45 PM", "instructor": "Linatti, L.", "status": "Open", "enrolled": 20, "capacity": 40},
            {"crn": "14911", "section": "002", "days": "TuTh", "time": "12:30 PM - 01:45 PM", "instructor": "Qui, X.", "status": "FULL", "enrolled": 40, "capacity": 40}
        ]
    },
    "COP 4530": {
        "title": "Data Structures and Algorithms",
        "sections": [
            {"crn": "14898", "section": "001", "days": "MW", "time": "02:00 PM - 03:15 PM", "instructor": "Korzhova, V.", "status": "Open", "enrolled": 32, "capacity": 40},
            {"crn": "14899", "section": "002", "days": "TuTh", "time": "02:00 PM - 03:15 PM", "instructor": "Kaleemurisa, E.", "status": "FULL", "enrolled": 40, "capacity": 40}
        ]
    },
    "MAC 2311": {
        "title": "Calculus I",
        "sections": [
            {"crn": "15001", "section": "001", "days": "MWF", "time": "10:00 AM - 10:50 AM", "instructor": "Martinez, C.", "status": "Open", "enrolled": 38, "capacity": 40},
            {"crn": "15002", "section": "002", "days": "TuTh", "time": "11:00 AM - 12:15 PM", "instructor": "Johnson, R.", "status": "Open", "enrolled": 25, "capacity": 40}
        ]
    }
}

# --- 4. TIME AND CONFLICT LOGIC (utility functions) ---

def time_to_minutes(time_str):
    """Converts a 12-hour time string to total minutes from midnight (0-1439)."""
    if not time_str or time_str.upper() in ["ASYNCHRONOUS", "ONLINE"]:
        return None
    
    match = re.match(r"(\d{1,2}):(\d{2})\s*(AM|PM)", time_str.upper())
    if not match:
        return None

    hours, minutes, ampm = match.groups()
    hours = int(hours)
    minutes = int(minutes)

    if ampm == 'PM':
        if hours != 12:
            hours += 12
    elif ampm == 'AM':
        if hours == 12:
            hours = 0

    return hours * 60 + minutes

def check_conflict(new_section, time_slot_map):
    """Checks for time conflicts with already scheduled classes."""
    if 'Online' in new_section['days']:
        return None

    start_min = time_to_minutes(new_section['start_time'])
    end_min = time_to_minutes(new_section['end_time'])
    
    if start_min is None or end_min is None:
        return None

    for day_abbr in new_section['days']:
        day_key = DAY_MAP.get(day_abbr)
        
        if day_key and day_key in time_slot_map:
            for existing_class in time_slot_map[day_key]:
                existing_start = time_to_minutes(existing_class['start_time'])
                existing_end = time_to_minutes(existing_class['end_time'])
                
                # Check for time overlap: (StartA < EndB) AND (StartB < EndA)
                if start_min < existing_end and existing_start < end_min:
                    return existing_class
    
    return None

def get_gpa_color(gpa):
    if gpa >= 3.7: return 'gpa-high'
    if gpa >= 3.2: return 'gpa-med'
    return 'gpa-low'

# --- 5. DATA SIMULATION (to replace live scraping) ---

def get_course_data_simulated(course_id):
    """Simulates looking up course sections and enriching data."""
    if course_id not in COURSE_OFFERINGS:
        return None, None

    course_info = COURSE_OFFERINGS[course_id]
    enriched_sections = []

    for section in course_info['sections']:
        instructor = section['instructor']
        time_parts = section['time'].split(' - ')
        
        # Parse days list for conflict check
        days = section['days']
        if days.lower() in ['online', 'asynchronous']:
            days_list = ['Online']
        else:
            days_list = re.findall(r'(Tu|Th|[MWF])', days) 

        enriched_sections.append({
            "course_id": course_id,
            "title": course_info['title'],
            "crn": section['crn'],
            "section": section['section'],
            "days": days_list,
            "time_str_raw": section['time'],
            "start_time": time_parts[0] if len(time_parts) >= 1 else section['time'],
            "end_time": time_parts[1] if len(time_parts) >= 2 else section['time'],
            "instructor": instructor,
            "status": section['status'],
            "avg_gpa": HISTORICAL_GRADES.get(instructor, 2.0)
        })
        
    # Sort by GPA (descending) then status (Open preferred)
    enriched_sections.sort(key=lambda x: (-x['avg_gpa'], x['status'] != 'Open')) 
    
    return course_info['title'], enriched_sections

# --- 6. UI INJECTION HELPERS (UPDATED GPA ICON) ---

def inject_review_section_html(section, status_type, conflict_info=None):
    """Generates the HTML for a single section card in the Step 2 review view."""
    
    if status_type == 'Selected':
        status_class = 'status-selected'
        status_tag = 'Auto-Selected'
        border_class = 'border-green-500'
        detail_text = "Best available non-conflicting section (Highest Avg GPA)."
    elif status_type == 'Conflict':
        status_class = 'status-conflict'
        status_tag = 'Time Conflict'
        border_class = 'border-red-500'
        detail_text = f"Time Conflict with {conflict_info['course_id']} ({conflict_info['title']})."
    else: # Available/Lower GPA/FULL
        status_class = 'status-available'
        status_tag = 'Available'
        border_class = 'border-gray-300'
        if section['status'] == 'FULL':
            status_tag = 'FULL'
            border_class = 'border-red-300'
        
        detail_text = ''

    gpa_color = get_gpa_color(section['avg_gpa'])

    return f"""
    <div class="p-4 rounded-lg border-2 {border_class} {'bg-green-50' if status_type == 'Selected' else 'bg-white'}">
        <span class="{status_class} text-white text-xs px-2 py-1 rounded-full mr-2">{status_tag}</span>
        Sec {section['section']} | Instructor: {section['instructor']}
        <span class="float-right {gpa_color} text-lg">⭐ {section['avg_gpa']:.2f}</span>
        <p class="text-sm text-gray-500">{section['days']} {section['time_str_raw']}</p>
        <p class="text-sm text-gray-500">{detail_text}</p>
        <p class="text-xs text-gray-400">CRN: {section['crn']}</p>
    </div>
    """

def inject_schedule_entry_html(section, priority, is_conflict=False):
    """Generates the HTML for the Current Schedule sidebar list."""
    gpa_color = get_gpa_color(section['avg_gpa'])
    return f"""
    <div class="p-3 schedule-entry {'conflict' if is_conflict else ''}">
        <p class="text-sm font-bold text-gray-900">{section['course_id']} ({section['title']})</p>
        <p class="text-xs text-gray-600">{section['days']} {section['time_str_raw']}</p>
        <p class="text-xs text-gray-600">Instructor: {section['instructor']} | <span class="{gpa_color}">Avg GPA: {section['avg_gpa']:.2f} ⭐</span></p>
    </div>
    """

def build_daily_schedule_data(schedule_data, user_courses):
    """
    Organizes scheduled sections into a dictionary grouped by day and sorted by time.
    """
    # Daily schedule keys 1-5 for Mon-Fri
    daily_schedule = {d: [] for d in range(1, 6)} 
    online_schedule = []

    for course_id, section in schedule_data.items():
        # Add priority index for reference
        section['priority'] = user_courses.index(course_id) + 1
        
        if 'Online' in section['days']:
            online_schedule.append(section)
            continue
        
        # Calculate start minutes for sorting
        section['start_minutes'] = time_to_minutes(section['start_time'])
        
        for day_abbr in section['days']:
            day_key = DAY_MAP.get(day_abbr)
            if day_key:
                daily_schedule[day_key].append(section)
    
    # Sort classes within each day by start time (in-place)
    for day_key in daily_schedule:
        daily_schedule[day_key].sort(key=lambda s: s['start_minutes'])
        
    return daily_schedule, online_schedule

def inject_daily_schedule_view(page, daily_schedule, online_schedule):
    """Injects the daily list view into the browser."""

    # Loop through Mon-Fri
    for day_key, day_id in DAY_ID_MAP.items():
        events_list = daily_schedule[day_key]
        
        if not events_list:
            page.evaluate(f"document.getElementById('{day_id}').innerHTML = 'No classes scheduled.'")
            continue
            
        day_html = ""
        for section in events_list:
            gpa_color = get_gpa_color(section['avg_gpa'])
            
            day_html += f"""
            <p class="text-sm border-l-2 border-green-500 pl-2">
                <span class="font-semibold text-gray-800">{section['time_str_raw']}</span>: 
                {section['course_id']} ({section['section']})<br>
                <span class="text-xs text-gray-600">Prof: {section['instructor']} | <span class="{gpa_color}">GPA: {section['avg_gpa']:.2f} ⭐</span></span>
            </p>
            """
        page.evaluate(f"document.getElementById('{day_id}').innerHTML = `{day_html}`")

    # Inject Online/Asynchronous classes
    online_html = ""
    if online_schedule:
        for section in online_schedule:
            gpa_color = get_gpa_color(section['avg_gpa'])
            online_html += f"""
            <p class="text-sm border-l-2 border-blue-500 pl-2">
                <span class="font-semibold text-gray-800">{section['course_id']}</span>: 
                Prof: {section['instructor']} | <span class="{gpa_color}">GPA: {section['avg_gpa']:.2f} ⭐</span>
            </p>
            """
        page.evaluate(f"document.getElementById('online-events').innerHTML = `{online_html}`")
    else:
        page.evaluate("document.getElementById('online-events').innerHTML = 'No online classes scheduled.'")


# --- 7. THE MAIN BOT EXECUTION LOGIC ---

def run_auto_scheduler_bot(url):
    
    selected_schedule = {}
    time_slot_map = {} 
    automation_results = {}
    
    print("="*70)
    print("🤖 USF INTELLIGENT REGISTRATION BOT")
    print("="*70)
    
    with sync_playwright() as p:
        print("\n1. Launching browser...")
        browser = p.chromium.launch(headless=False, slow_mo=500) 
        page = browser.new_page()
        
        print(f"2. Navigating to registration system...")
        page.goto(url)
        
        # --- PAUSE FOR USER INPUT ---
        print("\n" + "="*70)
        print("⏸️  WAITING FOR USER TO ENTER COURSES AND CLICK START")
        print("="*70)
        
        try:
            # Wait for the user to click the 'Start Automation' button
            page.wait_for_selector("#view-review:not(.hidden)", timeout=120000) 
        except:
            print("\n❌ Timeout waiting for user input. Please restart.")
            browser.close()
            return
        
        # READ THE USER'S COURSE LIST
        user_courses_raw = page.locator("#user-courses-input").inner_text()
        user_courses = [c.strip().upper() for c in user_courses_raw.split(',') if c.strip()]
        
        if not user_courses:
            print("❌ No courses entered.")
            browser.close()
            return

        print(f"\n✅ User input detected. Courses to schedule: {', '.join(user_courses)}")
        page.evaluate(f"document.getElementById('total-steps').textContent = '{len(user_courses)}'")
        
        # --- MAIN COURSE PROCESSING LOOP ---
        print("\n" + "="*70)
        print("🧠 STARTING INTELLIGENT COURSE SCHEDULING")
        print("="*70)
        
        for i, course_id in enumerate(user_courses):
            step = i + 1
            print(f"\n{'='*70}")
            print(f"📖 STEP {step}/{len(user_courses)}: {course_id}")
            
            course_title, live_sections = get_course_data_simulated(course_id)
            
            if not live_sections:
                automation_results[course_id] = {"status": "Error", "message": "Course data not found."}
                continue

            # --- UPDATE UI FOR CURRENT STEP ---
            page.evaluate(f"document.getElementById('current-step').textContent = '{step}'")
            page.evaluate(f"document.getElementById('review-course-id').textContent = '{course_id}'")
            page.evaluate(f"document.getElementById('review-course-title').textContent = '{course_title}'")
            page.evaluate("document.getElementById('sections-container').innerHTML = ''")
            page.evaluate("document.getElementById('decision-text').textContent = 'Analyzing all available sections...'")
            page.evaluate(f"document.getElementById('automation-countdown').textContent = 'Reviewing options for {course_id} | Automation will proceed in 4 seconds...'")
            time.sleep(0.5) 
            
            # Rank open sections
            open_sections = [s for s in live_sections if s['status'] == 'Open']
            
            # CONFLICT-AWARE SELECTION
            selected_section = None
            
            sections_html = ""
            
            for section in live_sections:
                is_full = section['status'] == 'FULL'
                is_open = section['status'] == 'Open'
                
                conflict = None
                
                if is_open:
                    conflict = check_conflict(section, time_slot_map)

                # --- Decision Logic and UI Generation ---
                if is_full:
                    sections_html += inject_review_section_html(section, 'FULL')
                elif conflict:
                    sections_html += inject_review_section_html(section, 'Conflict', conflict)
                elif selected_section is None and is_open and not conflict:
                    selected_section = section
                    sections_html += inject_review_section_html(section, 'Selected')
                else: 
                    sections_html += inject_review_section_html(section, 'Available') 
            
            page.evaluate(f"document.getElementById('sections-container').innerHTML = `{sections_html}`")

            # FINALIZE SELECTION
            if selected_section:
                selected_schedule[course_id] = selected_section
                
                # Update time slots for conflict checking
                if 'Online' not in selected_section['days']:
                    for day_abbr in selected_section['days']:
                        day_key = DAY_MAP.get(day_abbr)
                        if day_key:
                            if day_key not in time_slot_map:
                                time_slot_map[day_key] = []
                            time_slot_map[day_key].append(selected_section)
                
                automation_results[course_id] = {"status": "Scheduled", "section": selected_section}
                
                # Update Decision Banner
                page.evaluate(f"""
                    document.getElementById('decision-banner').classList.remove('bg-yellow-100', 'border-yellow-500', 'bg-red-100', 'border-red-500');
                    document.getElementById('decision-banner').classList.add('bg-green-100', 'border-green-500');
                    document.getElementById('decision-text').textContent = "The best section found is CRN {selected_section['crn']} with Prof. {selected_section['instructor']} (Avg GPA: {selected_section['avg_gpa']:.2f}).";
                """)
                
                # Inject to sidebar list
                schedule_list_html = inject_schedule_entry_html(selected_section, step)
                page.evaluate(f"document.getElementById('weekly-schedule-list').innerHTML += `{schedule_list_html}`")

            else:
                reason = "All open sections either full or conflict with higher priority courses."
                automation_results[course_id] = {"status": "Skipped", "message": reason}
                page.evaluate(f"""
                    document.getElementById('decision-banner').classList.remove('bg-yellow-100', 'border-yellow-500', 'bg-green-100', 'border-green-500');
                    document.getElementById('decision-banner').classList.add('bg-red-100', 'border-red-500');
                    document.getElementById('decision-text').textContent = "Skipped. All available sections had conflicts or were full.";
                """)

            # Countdown for the user to review the decision
            print(f"🤖 Automation paused for 10 seconds for UI review...")
            page.evaluate(f"document.getElementById('automation-countdown').textContent = 'Automation will proceed in 10 seconds...'")
            time.sleep(10)
        
        # --- FINAL RESULTS SUMMARY & BROWSER DISPLAY ---
        
        scheduled = len(selected_schedule)
        total = len(user_courses)

        # 1. HIDE REVIEW VIEW, SHOW FINAL SCHEDULE VIEW
        page.evaluate("document.getElementById('view-review').classList.add('hidden')")
        page.evaluate("document.getElementById('view-final').classList.remove('hidden')")
        
        # 2. UPDATE FINAL SUMMARY
        page.evaluate(f"document.getElementById('final-scheduled-count').textContent = '{scheduled}'")

        # 3. BUILD AND INJECT FINAL RESULTS ROWS (Left Panel)
        final_results_html = ""
        for course_id in user_courses:
            result = automation_results.get(course_id, {})
            section = result.get('section')
            
            if result.get('status') == 'Scheduled' and section:
                gpa_color = get_gpa_color(section['avg_gpa'])
                final_results_html += f"""
                <div class="p-4 rounded-lg border-2 border-green-500">
                    <p class="text-lg font-bold text-green-600">✔ {course_id} - {section['title']}</p>
                    <p class="text-sm text-gray-600">Scheduled {section['section']} with {section['instructor']} (<span class="{gpa_color}">Avg GPA: {section['avg_gpa']:.2f} ⭐</span>) | CRN {section['crn']} | {', '.join(section['days'])} {section['time_str_raw']}</p>
                </div>
                """
            else:
                final_results_html += f"""
                <div class="p-4 rounded-lg border-2 border-red-500 opacity-50">
                    <p class="text-lg font-bold text-red-600">✘ {course_id} - Skipped</p>
                    <p class="text-sm text-gray-600">Reason: {result.get('message', 'Unknown Error')}</p>
                </div>
                """
        
        page.evaluate(f"document.getElementById('final-results-container').innerHTML = `{final_results_html}`")

        # 4. BUILD AND INJECT DAILY SCHEDULE VIEW (Right Panel)
        daily_schedule, online_schedule = build_daily_schedule_data(selected_schedule, user_courses)
        inject_daily_schedule_view(page, daily_schedule, online_schedule)

        print("\n" + "="*70)
        print("✨ BOT COMPLETED - FINAL SCHEDULE DISPLAYED IN BROWSER!")
        print("="*70)
        
        page.evaluate("window.scrollTo(0, 0)")
        
        print("\nBrowser will remain open for review. Press Enter to close...")
        input()
        
        browser.close()


# --- 8. RUN THE BOT ---
# --- ADD THIS LINE BEFORE THE END OF THE FILE ---

if __name__ == "__main__":
    run_auto_scheduler_bot(DUMMY_REGISTRATION_URL)
    
