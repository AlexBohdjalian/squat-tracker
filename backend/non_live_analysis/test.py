from squat_analyser import SquatFormAnalyser

form_analyser = SquatFormAnalyser(model_complexity=2)

# alignment_video = 'backend/non_live_analysis/bad_alignment_example.mp4'
alignment_video = 0

temp_proc_file, final_summary = form_analyser.analyse(
    alignment_video,
    show_output=True
)


with open('backend/non_live_analysis/output.mp4', 'wb') as f:
    f.write(temp_proc_file.read())

import os
temp_proc_file.close()
os.unlink(temp_proc_file.name)
