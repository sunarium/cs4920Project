from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import itertools

font = ImageFont.truetype('arial', 25)
card_size = w, h = (150, 200)
piece_size = wp, hp = (75, 75)
bg_color = (255, 0, 0) # red
text_color = (0, 0, 0) # black

piece_names = ['\n'.join(x[::-1]) for x in itertools.product(['White', 'Black'], ['King', 'Queen', 'Bishop', 'Pawn', 'Knight', 'Rook'])]

for pn in piece_names:
    # card gen
    img = Image.new('RGB', card_size, bg_color)
    drawer = ImageDraw.Draw(img)
    drawer.line([0,0, w-1,0, w-1,h-1, 0,h-1, 0,0], width=5, fill=text_color)
    drawer.text((15, 15), font=font, text=pn, )
    filename = 'card_'+ pn.replace('\n', '_').lower() + '.png'
    with open(filename, 'wb') as f:
        img.save(f, format='png')
    del img, drawer

    # img = Image.new('RGB', piece_size, bg_color)
    # drawer = ImageDraw.Draw(img)
    # drawer.line([0,0, wp-1,0, wp-1,hp-1, 0,hp-1, 0,0], width=5, fill=text_color)
    # drawer.text((0, 10), font=font, text=pn, )
    # filename = 'piece_'+ pn.replace('\n', '_').lower() + '.png'
    # with open(filename, 'wb') as f:
    #     img.save(f, format='png')