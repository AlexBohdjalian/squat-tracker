from squat_analyser import SquatFormAnalyser

form_analyser = SquatFormAnalyser(model_complexity=2)

temp_proc_file, final_summary = form_analyser.analyse(0, show_output=True)
