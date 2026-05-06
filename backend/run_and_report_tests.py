import os
import threading
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import pytest
import subprocess
import platform

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ----------------- EXTENDED TEST METADATA -----------------
TESTS_DATA = [
    {"name": "test_upload_resume_success", "type": "Integration", "module": "test_resume.py", "input": "Assert: status_code == 201, 'resume_id' in json, skills contains ['Python', 'Java']"},
    {"name": "test_upload_resume_invalid_type", "type": "Integration", "module": "test_resume.py", "input": "Assert: status_code == 415, detail contains 'Only PDF and plain text files are supported'"},
    {"name": "test_get_resume_success", "type": "Integration", "module": "test_resume.py", "input": "Assert: status_code == 200, json['filename'] == 'test.txt', 'Python' in skills"},
    {"name": "test_get_resume_not_found", "type": "Integration", "module": "test_resume.py", "input": "Assert: status_code == 404, detail == 'Resume not found'"},
    {"name": "test_generate_questions_success", "type": "Integration", "module": "test_interview.py", "input": "Assert: status_code == 201, len(json['questions']) == 3, 'session_id' in json"},
    {"name": "test_generate_questions_resume_not_found", "type": "Integration", "module": "test_interview.py", "input": "Assert: status_code == 404, detail == 'Resume not found'"},
    {"name": "test_get_results_success", "type": "Integration", "module": "test_interview.py", "input": "Assert: status_code == 200, json['session_id'] == session_id, len(questions) == 1"},
    {"name": "test_get_results_not_found", "type": "Integration", "module": "test_interview.py", "input": "Assert: status_code == 404"},
    {"name": "test_evaluate_answer_success", "type": "Integration", "module": "test_evaluation.py", "input": "Assert: status_code == 201, 'evaluation_id' in json, similarity_score > 0"},
    {"name": "test_evaluate_answer_question_not_found", "type": "Integration", "module": "test_evaluation.py", "input": "Assert: status_code == 404, detail == 'Question not found'"},
    
    {"name": "test_predict_load", "type": "Integration", "module": "test_system.py", "input": "Assert: status_code == 200, json['status'] == 'ok', 'prediction_rpm' in json"},
    {"name": "test_load_summary", "type": "Integration", "module": "test_system.py", "input": "Assert: status_code == 200, 'avg_rpm' in json, 'error_rate_pct' in json"},
    {"name": "test_recommend_resources", "type": "Integration", "module": "test_system.py", "input": "Assert: status_code == 200, 'recommended_workers' in json, json['status'] == 'ok'"},
    {"name": "test_detect_anomalies", "type": "Integration", "module": "test_system.py", "input": "Assert: status_code == 200, 'anomaly_count' in json, 'spikes' in json"},
    {"name": "test_scheduler_status", "type": "Integration", "module": "test_system.py", "input": "Assert: status_code == 200, 'active_jobs' in json, 'worker_health' == 'healthy'"},
    {"name": "test_dashboard", "type": "Integration", "module": "test_system.py", "input": "Assert: status_code == 200, 'system_health' in json, 'load_prediction' in json"},

    {"name": "test_evaluate_answer_high_similarity", "type": "Unit", "module": "test_answer_evaluator.py", "input": "Assert: similarity_score > 0.7, normalized_score > 70, feedback is str"},
    {"name": "test_evaluate_answer_low_similarity", "type": "Unit", "module": "test_answer_evaluator.py", "input": "Assert: similarity_score < 0.4, normalized_score < 40, weak_areas is list"},
    {"name": "test_evaluate_answer_empty_user_answer", "type": "Unit", "module": "test_answer_evaluator.py", "input": "Assert: normalized_score < 30, feedback contains 'Weak answer'"},
    {"name": "test_extract_skills", "type": "Unit", "module": "test_resume_analyzer.py", "input": "Assert: skills contains 'Python' and 'Java'"},
    {"name": "test_detect_anomalies_and_spikes", "type": "Unit", "module": "test_anomaly_detector.py", "input": "Assert: status == 'ok', total_requests_analysed == 42, anomaly_count > 0"},
    {"name": "test_z_score_zero_std", "type": "Unit", "module": "test_anomaly_detector.py", "input": "Assert: len(res) == 3, all(x == 0 for x in res)"},
    {"name": "test_detect_empty", "type": "Unit", "module": "test_anomaly_detector.py", "input": "Assert: status == 'insufficient_data'"},
    {"name": "test_load_predictor_success", "type": "Unit", "module": "test_load_predictor.py", "input": "Assert: status == 'ok', current_rpm == 1.0, len(forecast) == 5"},
    {"name": "test_load_levels", "type": "Unit", "module": "test_load_predictor.py", "input": "Assert: levels are ['low', 'medium', 'high', 'critical'] for specific RPMs"},
    {"name": "test_trends", "type": "Unit", "module": "test_load_predictor.py", "input": "Assert: trends are ['increasing', 'decreasing', 'stable'] based on gradients"},
    {"name": "test_resource_allocator_normal_load", "type": "Unit", "module": "test_resource_allocator.py", "input": "Assert: status == 'ok', recommended_workers == 6, reasoning is str"},
    {"name": "test_get_db_generator", "type": "Unit", "module": "test_misc.py", "input": "Assert: next(gen) is not None (SQLAlchemy Session object)"},
    {"name": "test_resume_analyzer_pdf", "type": "Unit", "module": "test_misc.py", "input": "Assert: 'Python' and 'Java' in extracted text from mocked PDF"},
    {"name": "test_job_scheduler_failure", "type": "Unit", "module": "test_misc.py", "input": "Assert: raises RuntimeError containing 'job failed'"},
    {"name": "test_job_scheduler_history_limit", "type": "Unit", "module": "test_misc.py", "input": "Assert: len(scheduler._history) <= 200 after 250 jobs"},
    {"name": "test_answer_evaluator_exception", "type": "Unit", "module": "test_misc.py", "input": "Assert: raises Exception ('model error') when _get_model is mocked to fail"}
]



class TestTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("InterviewIQ - Ultimate Test Suite")
        self.geometry("1150x750")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Tabs
        self.tabview = ctk.CTkTabview(self, segmented_button_selected_color="#3498db")
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.tab_runner = self.tabview.add("Test Selector")
        self.tab_details = self.tabview.add("Execution & Stats")
        
        self.setup_runner_tab()
        self.setup_details_tab()
        
        self.test_checkboxes = {}
        self.test_results = {}
        self.populate_tests()
        
        self.is_running = False

    def setup_runner_tab(self):
        self.tab_runner.grid_rowconfigure(1, weight=1)
        self.tab_runner.grid_columnconfigure(0, weight=1)
        
        header_frame = ctk.CTkFrame(self.tab_runner, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        header = ctk.CTkLabel(header_frame, text="Available Test Suite", font=ctk.CTkFont(size=24, weight="bold"))
        header.pack(side="left", padx=10)
        
        # Scrollable list
        self.scroll_frame = ctk.CTkScrollableFrame(self.tab_runner, fg_color="#1a1a1a")
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(1, weight=1)
        
        # Controls
        ctrl_frame = ctk.CTkFrame(self.tab_runner, fg_color="#222")
        ctrl_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        self.btn_run_selected = ctk.CTkButton(ctrl_frame, text="RUN SELECTED", fg_color="#27ae60", hover_color="#2ecc71", command=self.run_selected)
        self.btn_run_selected.pack(side="left", padx=15, pady=15)
        
        self.btn_run_all = ctk.CTkButton(ctrl_frame, text="RUN ALL", fg_color="#2980b9", hover_color="#3498db", command=self.run_all)
        self.btn_run_all.pack(side="left", padx=15, pady=15)

        self.btn_terminal = ctk.CTkButton(ctrl_frame, text="RUN IN TERMINAL", fg_color="#8e44ad", hover_color="#9b59b6", command=self.run_in_terminal)
        self.btn_terminal.pack(side="left", padx=15, pady=15)
        
        self.lbl_status_main = ctk.CTkLabel(ctrl_frame, text="IDLE", font=ctk.CTkFont(size=14, weight="bold"), text_color="gray")
        self.lbl_status_main.pack(side="right", padx=20)

    def setup_details_tab(self):
        self.tab_details.grid_rowconfigure(1, weight=1)
        self.tab_details.grid_columnconfigure(0, weight=1)
        self.tab_details.grid_columnconfigure(1, weight=2)
        
        # Top Stats Banner
        stats_banner = ctk.CTkFrame(self.tab_details, fg_color="#222", corner_radius=10)
        stats_banner.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        self.progress = ctk.CTkProgressBar(stats_banner, width=400, height=15, progress_color="#3498db")
        self.progress.set(0)
        self.progress.pack(side="left", padx=20, pady=20)
        
        self.lbl_pct = ctk.CTkLabel(stats_banner, text="0%", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_pct.pack(side="left", padx=5)
        
        self.lbl_counts = ctk.CTkLabel(stats_banner, text="Passed: 0 | Failed: 0", font=ctk.CTkFont(size=14))
        self.lbl_counts.pack(side="right", padx=20)
        
        # Left pane: List
        self.list_frame = ctk.CTkScrollableFrame(self.tab_details, label_text="Execution Log", fg_color="#1a1a1a")
        self.list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Right pane: Details
        self.detail_frame = ctk.CTkFrame(self.tab_details, fg_color="#222")
        self.detail_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.detail_frame.grid_rowconfigure(5, weight=1)
        self.detail_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.detail_frame, text="Test Report", font=ctk.CTkFont(size=22, weight="bold"), text_color="#3498db").grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.lbl_det_name = ctk.CTkLabel(self.detail_frame, text="Select a test to view full report...", font=ctk.CTkFont(size=16))
        self.lbl_det_name.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.lbl_det_type = ctk.CTkLabel(self.detail_frame, text="", text_color="gray")
        self.lbl_det_type.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        self.lbl_det_status = ctk.CTkLabel(self.detail_frame, text="", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_det_status.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        
        self.lbl_det_time = ctk.CTkLabel(self.detail_frame, text="")
        self.lbl_det_time.grid(row=4, column=0, padx=20, pady=5, sticky="w")
        
        self.lbl_det_input = ctk.CTkTextbox(self.detail_frame, height=250, fg_color="#111", border_color="#333", border_width=1, font=ctk.CTkFont(family="Consolas", size=12))
        self.lbl_det_input.grid(row=5, column=0, padx=20, pady=20, sticky="nsew")


    def populate_tests(self):
        for i, t in enumerate(TESTS_DATA):
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(self.scroll_frame, text=t['name'], variable=var, font=ctk.CTkFont(size=13))
            cb.grid(row=i, column=0, padx=20, pady=8, sticky="w")
            
            color = "#9b59b6" if t['type'] == "Integration" else "#3498db"
            badge = ctk.CTkLabel(self.scroll_frame, text=f" {t['type']} ", fg_color=color, text_color="white", corner_radius=6, font=ctk.CTkFont(size=11, weight="bold"))
            badge.grid(row=i, column=1, padx=20, pady=8, sticky="e")
            
            self.test_checkboxes[t['name']] = var

    def show_test_details(self, test_name):
        res = self.test_results.get(test_name, {})
        meta = next((t for t in TESTS_DATA if t['name'] in test_name), {})
        
        self.lbl_det_name.configure(text=f"TEST: {test_name.upper()}")
        self.lbl_det_type.configure(text=f"MODULE: {meta.get('module', 'Unknown')}  |  SCENARIO: {meta.get('type', 'Unit')}")
        
        outcome = res.get('outcome', 'UNKNOWN')
        color = "#2ecc71" if outcome == "PASSED" else "#e74c3c" if outcome == "FAILED" else "#f39c12"
        self.lbl_det_status.configure(text=f"STATUS: {outcome}", text_color=color)
        self.lbl_det_time.configure(text=f"EXECUTION TIME: {res.get('duration', '-')} seconds")
        
        self.lbl_det_input.delete("0.0", "end")
        report_text = f"TECHNICAL ASSERTIONS:\n{meta.get('input', 'N/A')}\n\n"
        
        # Always show headers for consistency, use 'No output' as fallback
        report_text += "--- CAPTURED OUTPUT (STDOUT) ---\n"
        report_text += res.get('stdout') if res.get('stdout') else "No stdout captured."
        report_text += "\n\n"
            
        report_text += "--- SYSTEM LOGS (CAPLOG) ---\n"
        report_text += res.get('system_logs') if res.get('system_logs') else "No system logs captured."
        report_text += "\n\n"
            
        if res.get('stderr'):
            report_text += "--- CAPTURED ERRORS (STDERR) ---\n"
            report_text += res['stderr'] + "\n\n"
            
        if res.get('longrepr'):
            report_text += "--- FAILURE TRACEBACK ---\n"
            report_text += res['longrepr'] + "\n"


            
        self.lbl_det_input.insert("0.0", report_text)


    def run_selected(self):
        if self.is_running: return
        selected = [k for k, v in self.test_checkboxes.items() if v.get()]
        self.start_test_thread(selected)

    def run_all(self):
        if self.is_running: return
        self.start_test_thread([k for k in self.test_checkboxes.keys()])

    def run_in_terminal(self):
        selected = [k for k, v in self.test_checkboxes.items() if v.get()]
        if not selected: return
        
        k_filter = " or ".join(selected)
        
        if platform.system() == "Windows":
            # Using CREATE_NEW_CONSOLE is much cleaner than 'start cmd /k' as it avoids shell quoting issues
            subprocess.Popen(
                ["python", "-m", "pytest", "tests/", "-v", "-k", k_filter],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Linux/macOS
            cmd = f'python3 -m pytest tests/ -v -k "{k_filter}"'
            subprocess.Popen(["x-terminal-emulator", "-e", cmd] if platform.system() == "Linux" else ["terminal", cmd])

    def start_test_thread(self, test_list):
        if not test_list: return
        self.is_running = True
        self.tabview.set("Execution & Stats")
        self.lbl_status_main.configure(text="RUNNING...", text_color="#f39c12")
        
        # Reset UI
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        self.test_results.clear()
        self.progress.set(0)
        self.lbl_pct.configure(text="0%")
        self.lbl_counts.configure(text="Passed: 0 | Failed: 0")
        
        self.total_to_run = len(test_list)
        self.passed = 0
        self.failed = 0
        self.completed_count = 0
        
        # -v: verbose, -rA: show extra test summary for ALL (passed, failed, etc.)
        args = ["-v", "-rA", "--disable-warnings"]
        
        # Only use -k if we are NOT running the full suite.
        # This prevents pytest from deselecting tests not in our hardcoded list.
        if len(test_list) < len(self.test_checkboxes):
            args.append("-k")
            args.append(" or ".join(test_list))
        
        threading.Thread(target=self._test_thread_worker, args=(args,), daemon=True).start()


    def _test_thread_worker(self, args):
        app_instance = self
        class RealTimePlugin:
            def pytest_collection_finish(self_plugin, session):
                app_instance.after(0, app_instance.set_total_count, len(session.items))
            def pytest_runtest_setup(self_plugin, item):
                app_instance.after(0, app_instance.on_test_started, item.nodeid)
            def pytest_runtest_logreport(self_plugin, report):
                # Count 'call' (the test itself) or a failed 'setup' (which means the test never ran)
                # Also count 'skipped' tests so the progress bar completes
                if report.when == 'call' or (report.when == 'setup' and report.outcome != 'passed'):
                    app_instance.after(0, app_instance.on_test_completed, report)
        
        pytest.main(args, plugins=[RealTimePlugin()])
        self.after(0, self.on_all_tests_completed)

    def set_total_count(self, count):
        self.total_to_run = count
        if self.total_to_run == 0: self.total_to_run = 1 # Avoid div by zero


    def on_test_started(self, nodeid):
        test_name = nodeid.split("::")[-1]
        self.test_results[test_name] = {'outcome': 'RUNNING', 'duration': '-'}
        btn = ctk.CTkButton(self.list_frame, text=f"  ⏳  {test_name}", fg_color="#34495e", hover_color="#2c3e50", anchor="w",
                            command=lambda t=test_name: self.show_test_details(t))
        btn.pack(fill="x", padx=5, pady=3)
        self.test_results[f"{test_name}_btn"] = btn

    def on_test_completed(self, report):
        test_name = report.nodeid.split("::")[-1]
        outcome = report.outcome.upper()
        dur = round(report.duration, 3)
        
        # Capture logs from attributes and all sections
        stdout = getattr(report, 'capstdout', "")
        stderr = getattr(report, 'capstderr', "")
        system_logs = ""
        
        # Pytest stores output in sections as (name, content) tuples
        for section_name, content in report.sections:
            low_name = section_name.lower()
            if "stdout" in low_name:
                if content not in stdout: stdout += content
            elif "stderr" in low_name:
                if content not in stderr: stderr += content
            elif "log" in low_name:
                if content not in system_logs: system_logs += content

                
        longrepr = str(report.longrepr) if report.longrepr else ""
        
        self.test_results[test_name] = {
            'outcome': outcome, 
            'duration': dur,
            'stdout': stdout,
            'stderr': stderr,
            'system_logs': system_logs,
            'longrepr': longrepr
        }


        btn = self.test_results.get(f"{test_name}_btn")

        
        if btn:
            if outcome == "PASSED":
                btn.configure(text=f"  ✔  {test_name}", fg_color="#27ae60", hover_color="#2ecc71")
                self.passed += 1
            elif outcome == "FAILED":
                btn.configure(text=f"  ✖  {test_name}", fg_color="#c0392b", hover_color="#e74c3c")
                self.failed += 1
            else: # SKIPPED
                btn.configure(text=f"  ↷  {test_name}", fg_color="#f39c12", hover_color="#e67e22")
                # We don't increment passed or failed for skips
        
        self.completed_count += 1
        prog = self.completed_count / self.total_to_run
        self.progress.set(prog)
        self.lbl_pct.configure(text=f"{int(prog * 100)}%")
        self.lbl_counts.configure(text=f"Passed: {self.passed} | Failed: {self.failed}")


    def on_all_tests_completed(self):
        self.is_running = False
        self.lbl_status_main.configure(text="COMPLETE", text_color="#27ae60")

if __name__ == "__main__":
    app = TestTrackerApp()
    app.mainloop()
