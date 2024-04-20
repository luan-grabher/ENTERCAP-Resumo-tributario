import markdown
import webbrowser

def mostrar_manual():
    manual_md_path = 'manual.md'
    
    manual_html_convertido = 'manual.html'
    
    with open(manual_md_path, 'r') as f:
        manual_md = f.read()
        
    manual_html = markdown.markdown(manual_md)
    manual_html = f'<html><head><link rel="stylesheet" type="text/css" href="manual.css"></head><body>{manual_html}</body></html>'
    
    with open(manual_html_convertido, 'w') as f:
        f.write(manual_html)
        
    webbrowser.open(manual_html_convertido)    
    
    return


if __name__ == '__main__':
    mostrar_manual()