import StringIO
from PIL import Image

class Modifier(object):
    def __init__(self, image, params):
        self.image = image
        self.params = params

    def run(self):
        return self

class SizeModifier(Modifier):
    """
    Modifies the physical dimensions of an image. Will keep the image ratio if either
    `width` or `height` is provided and warp the ratio if both are provided

    Params:
    - width: integer value indicating the desired width, in pixels
    - height: integer value indicating the desired height, in pixels
    """

    def run(self):
        if self.params.get('width') or self.params.get('height'):
            image_ratio = self.image.size[0] / float(self.image.size[1]) #  width / height

            # determine the width and height values
            if self.params.get('width') and self.params.get('height'):
                width = int(float(self.params['width']))
                height = int(float(self.params['height']))
            elif self.params.get('width'):
                width = int(float(self.params['width']))
                height = int(width / image_ratio)
            elif self.params.get('height'):
                height = int(float(self.params['height']))
                width = int(height * image_ratio)
            else:
                raise Exception('Internal Error. Something really strange happened')
            
            # apply new width and height values
            self.image = self.image.resize((width, height))

        return self

class QualityModifier(Modifier):
    """
    Modifies the quality (and file size) of the image

    Params:
    - quality: 0-100 integer value representing the desired quality
    """

    def run(self):
        if self.params.get('quality') and not float(self.params.get('quality')) >= 100:
            quality = int(float(self.params['quality']))

            # PIL can only apply a quality change during the save method, so we need to
            # save the modified image to a string buffer and then re-initialize it. This
            # is kind of stupid and slow, so there may be a better way
            quality_modified_data = StringIO.StringIO()
            self.image.save(quality_modified_data, 'jpeg', quality=quality)
            quality_modified_data.seek(0)
            self.image = Image.open(quality_modified_data)

        return self
