
**Submitting merge requests**

When submitting a merge request, please indicate which issue you're addressing. Make sure that you've run Black on your code before submitting it. To learn more about updating repositories with your edited code, see GIT_TUTORIALS.md.


**Using Python Black**

Black is a Python code formatter. Run `pip install black` in your terminal. Black must be run against a Python file: `black <file_name>`.
When Black is done running, it will output the following:

​       reformatted long_func.py
​      All done! ✨ 🍰 ✨ 1 file reformatted.

This indicates that the file has been reformatted following PEP8 guidelines. If you don't want your file to be reformatted, but you'd still like to see the changes Black suggests, run the formatter with the flag `--diff`.