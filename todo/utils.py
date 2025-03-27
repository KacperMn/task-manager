from django.utils.text import slugify

def generate_unique_slug(base_name, user_id, model_class):
    """Generate a unique slug based on name and user_id."""
    base_slug = slugify(base_name)
    slug = f"{base_slug}-{user_id}"
    counter = 1
    while model_class.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{user_id}-{counter}"
        counter += 1
    return slug