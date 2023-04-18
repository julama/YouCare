html_string = f"""
        <script>
        Array.from(window.parent.document.querySelectorAll('div[data-testid="stExpander"] div[role="button"] p')).find(el => el.innerText === '{0}').classList.add({1});
        console.log("test");
        </script>
        """