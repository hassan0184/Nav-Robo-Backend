from rest_framework.renderers import JSONRenderer


# todo make a seperate module for exceptions and success message wrapper

class SuccessJResponse(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not renderer_context['response'].exception:
            # in case of no exception use this wrapper else use the drf-standardize-errors package
            data = {
                "success": True,
                "data": data
            }
            return super(SuccessJResponse, self).render(data, accepted_media_type, renderer_context)
        return super(SuccessJResponse, self).render(data, accepted_media_type, renderer_context)
