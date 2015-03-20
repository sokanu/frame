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
                desired_width = int(float(self.params['width']))
                desired_height = int(float(self.params['height']))
                width, height = self.calculate_minimum_height_width(self.image.size[0], self.image.size[1], desired_width, desired_height)
                offset_x, offset_y = self.calculate_x_y_crop_offsets(width, height, desired_width, desired_height)
                self.image = self.image.resize((width, height))
                self.image = self.image.crop((offset_x, offset_y, offset_x + desired_width, offset_y + desired_height))
            elif self.params.get('width'):
                width = int(float(self.params['width']))
                height = int(width / image_ratio)
                # apply new width and height values
                self.image = self.image.resize((width, height))
            elif self.params.get('height'):
                height = int(float(self.params['height']))
                width = int(height * image_ratio)
                # apply new width and height values
                self.image = self.image.resize((width, height))
            else:
                raise Exception('Internal Error. Something really strange happened')
            
        return self

    @staticmethod
    def calculate_minimum_height_width(image_width, image_height, desired_width, desired_height):
        """
        Takes a current image width & height, as well as a desired width & height
        Returns a (width, height) tuple that returns the minimum width & height values
        that will work for the desired_width & desired_height, while maintaining image ratio
        """
        image_width, image_height = float(image_width), float(image_height)
        desired_width, desired_height = float(desired_width), float(desired_height)

        # resize the width and height to match the desired height, while maintaining ratio
        scaled_width = desired_height / image_height * image_width
        scaled_height = desired_height

        # if the new width is below the desired width, scale up to match width
        if scaled_width < desired_width:
            scaled_height = desired_width / scaled_width * scaled_height
            scaled_width = desired_width

        scaled_width, scaled_height = int(scaled_width), int(scaled_height)
        return scaled_width, scaled_height

    @staticmethod
    def calculate_x_y_crop_offsets(image_width, image_height, desired_width, desired_height):
        """
        Takes a current image width & height, as well as a desired width & height
        Returns the offset x & y positions needed when cropping an image down the center
        """
        offset_x = float(image_width - desired_width) / 2
        offset_y = float(image_height - desired_height) / 2

        offset_x, offset_y = int(offset_x), int(offset_y)
        return offset_x, offset_y


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
