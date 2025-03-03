### NON-USED CODE ###

from pyflowchart import Flowchart
import textwrap
import webbrowser

# Your sample code
sample_code = textwrap.dedent("""
    def find_id_code(text: str) -> str:
        result = ""
        for i in range(len(text)):
            char = text[i]
            if char.isdigit():
                result += char
        if len(result) > 11:
            return "Too many numbers!"
        elif len(result) < 11:
            return "Not enough numbers!"
        return result
""")

# 1. Create a flowchart from code
fc = Flowchart.from_code(sample_code)

# 2. Get the DSL string
flowchart_dsl = fc.flowchart()

# 3. Prepare a minimal HTML page that includes flowchart.js and your DSL
html_template = f"""
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/raphael/2.3.0/raphael.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/flowchart/1.15.0/flowchart.min.js"></script>
</head>
<body>
  <div id="canvas" style="width: 800px; height: 600px;"></div>
  <script>
    var code = `{flowchart_dsl}`;
    var chart = flowchart.parse(code);
    chart.drawSVG('canvas');
  </script>
</body>
</html>
"""

# 4. Write that HTML to a file
filename = "flowchart_example.html"
with open(filename, "w", encoding="utf-8") as f:
    f.write(html_template)

# 5. Automatically open the file in your default browser
webbrowser.open(filename)