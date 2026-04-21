import base64
import streamlit as st
import streamlit.components.v1 as components

def trigger_bulk_download(files_info: list):
    """
    Trigger multiple browser downloads using JavaScript.
    files_info: list of dicts with {'name': 'filename.png', 'data': b'binary_data'}
    """
    if not files_info:
        return

    js_code = """
    <script>
    async function downloadFiles(files) {
        for (const file of files) {
            const link = document.createElement('a');
            link.href = 'data:image/png;base64,' + file.base64;
            link.download = file.name;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            // Small delay to prevent browser from blocking too many rapid downloads
            await new Promise(resolve => setTimeout(resolve, 300));
        }
    }
    
    // The data will be injected into this script
    const filesToDownload = %FILES_JSON%;
    downloadFiles(filesToDownload);
    </script>
    """
    
    # Prepare serializable list
    serializable_files = []
    for f in files_info:
        b64 = base64.b64encode(f['data']).decode('utf-8')
        serializable_files.append({
            'name': f['name'],
            'base64': b64
        })
    
    import json
    js_final = js_code.replace("%FILES_JSON%", json.dumps(serializable_files))
    
    # Use a small hidden component to execute JS
    components.html(js_final, height=0, width=0)

def render_gallery_item(file_path, name):
    """Render a single image card in a gallery"""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            
        st.image(data, use_container_width=True, caption=name)
        st.download_button(
            label=f"⬇️ Download",
            data=data,
            file_name=name,
            mime="image/png",
            key=f"dl_{name}",
            width="stretch"
        )
    except Exception as e:
        st.error(f"Error loading {name}: {e}")
