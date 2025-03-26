def layout_context(request):
    """Add default navbar and footer visibility settings"""
    return {
        'show_navbar': False,  # Default to not showing navbar
        'show_footer': False   # Default to not showing footer
    }