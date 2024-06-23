import wikipedia

def get_wikipedia_info(query):
    try:
        page = wikipedia.page(query)
        summary = page.summary
        images = page.images[:3]  # Limit to the first 3 images
        content = page.content.split("== References ==")[0]
        return {
            'summary': summary,
            'images': images,
            'content': content,
            'captions': [img.split('/')[-1].replace('_', ' ') for img in images]
        }
    except wikipedia.exceptions.DisambiguationError as e:
        return {'error': f"Disambiguation error: {str(e)}"}
    except wikipedia.exceptions.PageError:
        return {'error': 'No information found'}
    except Exception as e:
        return {'error': f"An error occurred: {str(e)}"}
