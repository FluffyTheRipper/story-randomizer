import json
import jsonpickle
from classes import *
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import *
from reportlab.lib.units import inch, cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


PDF_WIDTH=612.0
PDF_HEIGHT=792.0

HEADER_COLOR = lightgrey
HEADER_TEXT_COLOR = whitesmoke

BODY_COLOR = white
BODY_TEXT_COLOR = black

CHARACTER_TRAITS = ['Conscience',
                    'Consider',
                    'Controlled',
                    'Disbelief',
                    'Faith',
                    'Feeling',
                    'Help',
                    'Hinder',
                    'Logic',
                    'Oppose',
                    'Persue',
                    'Prevent',
                    'Reconsider',
                    'Support',
                    'Temptation',
                    'Uncontrolled']

dynamic_headings = ["Resolve",
                    "Growth",
                    "Approach",
                    "Mental Sex",
                    "OS Driver",
                    "OS Limit",
                    "OS Outcome",
                    "MC Judgement"
                    ]

abstract_headings = ["Goal",
											"Requirements",
											"Consequences",
											"Forewarnings",
											"Dividends",
											"Costs",
											"Prerequisites",
											"Preconditions"
											]

num_cols = 4
margin = 0.5*inch

VERT_PADDING = 0.5*inch

styles = getSampleStyleSheet()
table_cell_style = ParagraphStyle('yourtitle', alignment=1)

# Breaks list into list of lists with number of elements per row, see below
# data = [['00', '01', '02', '03', '04'],
#         ['10', '11', '12', '13', '14'],
def chunk(lst,n):
	for i in range(0, len(lst), n):
		yield lst[i:i + n]

def stripe_lists(a, b):
	result = [None]*(len(a)+len(b))
	result[::2] = a
	result[1::2] = b

	return result

def striped_table(listA,listB):
	alt_join = stripe_lists(listA, listB)
	table_data = []

	for row in alt_join:
		new_row = []
		for item in row:
			content = Paragraph(item, table_cell_style)
			new_row.append(content)
		table_data.append(new_row)

	t=Table(table_data, colWidths=(PDF_WIDTH-2*margin)/num_cols)

	for each in range(len(alt_join)):
		if each % 2 == 0:
			bg_color = HEADER_COLOR
			txt_color = HEADER_TEXT_COLOR
		else:
			bg_color = BODY_COLOR
			txt_color = BODY_TEXT_COLOR

		t.setStyle(TableStyle([ ('BACKGROUND',(0,each),(num_cols,each),bg_color),
														('TEXTCOLOR',(0,0),(num_cols,0),txt_color),
														('ALIGN',(0,0),(-1,-1),'CENTER'),
														('BOX',(0,0),(-1,-1),0.25, black),
														('INNERGRID',(0,0),(-1,-1),0.25,black),
														('VALIGN',(0,0),(-1,-1),'MIDDLE'),
														('LEFTPADDING',(0,0),(-1,-1),2),
														('RIGHTPADDING',(0,0),(-1,-1),2),
														('BOTTOMPADDING',(0,0),(-1,-1),2),
														('TOPPADDING',(0,0),(-1,-1),2)
														]))
	return t

def vert_table(listA, listB, cols):
	listC = []
	for i in range(len(listA)):
		row = []
		row.append(listA[i])
		row.append(listB[i])
		listC.append(row)

	table_data = []
	for row in listC:
		new_row = []
		for item in row:
			content = Paragraph(item, table_cell_style)
			new_row.append(content)
		table_data.append(new_row)

	t=Table(table_data, colWidths=(PDF_WIDTH-2*margin)/cols)

	t.setStyle(TableStyle([ ('BACKGROUND',(0,0),(0,4),HEADER_COLOR),
													('TEXTCOLOR',(0,0),(2,0),black),
													('ALIGN',(0,0),(-1,-1),'CENTER'),
													('BOX',(0,0),(-1,-1),0.25, black),
													('INNERGRID',(0,0),(-1,-1),0.25,black),
													('VALIGN',(0,0),(-1,-1),'MIDDLE'),
													('LEFTPADDING',(0,0),(-1,-1),2),
													('RIGHTPADDING',(0,0),(-1,-1),2),
													('BOTTOMPADDING',(0,0),(-1,-1),2),
													('TOPPADDING',(0,0),(-1,-1),2)
													]))
	return t


def through_table(data):
	styles = getSampleStyleSheet()
	table_cell_style = ParagraphStyle('yourtitle', alignment=1)

	table_data = []
	for row in data:
		new_row = []
		for item in row:
			content = Paragraph(item, table_cell_style)
			new_row.append(content)
		table_data.append(new_row)

	t=Table(table_data, colWidths=(PDF_WIDTH-2*margin)/5)

	t.setStyle(TableStyle([ ('BACKGROUND',(0,0),(0,-1),HEADER_COLOR),
													('BACKGROUND',(0,0),(-1,0),HEADER_COLOR),
													('TEXTCOLOR',(0,0),(2,0),black),
													('ALIGN',(0,0),(-1,-1),'CENTER'),
													('BOX',(0,0),(-1,-1),0.25, black),
													('INNERGRID',(0,0),(-1,-1),0.25,black),
													('VALIGN',(0,0),(-1,-1),'MIDDLE'),
													('LEFTPADDING',(0,0),(-1,-1),2),
													('RIGHTPADDING',(0,0),(-1,-1),2),
													('BOTTOMPADDING',(0,0),(-1,-1),2),
													('TOPPADDING',(0,0),(-1,-1),2)
													]))
	return t

def check_newpage(height, canv):
	if height < 0.0:
		canv.showPage()
		canv.setFont("Helvetica-Bold", 10)
		return True
	else:
		return False

def save(path, save_path):
	with open(path) as json_file:
		in_data = json.load(json_file)

	canvas = Canvas(save_path[0], pagesize=LETTER)
	canvas.setFont("Helvetica-Bold", 10)

	# ============== TABLE 1
	characters = []
	for c in in_data['characters']:
		characters.append(jsonpickle.decode(c))

	t_traits = []
	for trait in CHARACTER_TRAITS:
		c_list = []
		for c in characters:
			if trait in c.traits:
				c_list.append(c.name)
		t_traits.append((", ").join(c_list))

	a = []
	b = []

	for item in chunk(CHARACTER_TRAITS,num_cols): a.append(item)
	for item in chunk(t_traits,num_cols): b.append(item)

	curr_height = PDF_HEIGHT-margin
	table1 = striped_table(a,b)
	w,h = table1.wrap(0,0)	
	canvas.drawString(margin,curr_height+2, "Table 1 - Trait Distribution")
	curr_height -= h
	table1.wrapOn(canvas, margin,curr_height)
	table1.drawOn(canvas, margin,curr_height)
	curr_height -= VERT_PADDING

	# ============== TABLE 2
	c_names = []
	c_traits = []
	temp = []

	# Traits are fucky, okay.
	for l_traits in in_data['character_traits']:
		temp.append((", ").join(l_traits))

	for item in chunk(in_data['character_names'],num_cols): c_names.append(item)
	for item in chunk(temp,num_cols): c_traits.append(item)

	table2 = striped_table(c_names,c_traits)
	w,h = table2.wrap(0,0)
	if check_newpage((curr_height - h),canvas):
		curr_height = PDF_HEIGHT-margin

	canvas.drawString(margin,curr_height+2, "Table 2 - Characters")
	curr_height -= h	
	table2.wrapOn(canvas, margin,curr_height)
	table2.drawOn(canvas, margin,curr_height)
	curr_height -= VERT_PADDING

	# ============== TABLE 3 & 4
	# Check for blank data
	for i, dyn in enumerate(in_data['dynamics']):
		if not dyn:
			in_data['dynamics'][i] = '--'

	# Duplicate entries in main program append a 1 to this entry, so remove that
	in_data['dynamics'][7] = in_data['dynamics'][7][:-1]

	table3 = vert_table(dynamic_headings[0:4], in_data['dynamics'][0:4],5)
	table4 = vert_table(dynamic_headings[4:8], in_data['dynamics'][4:8],5)
	w,h = table3.wrap(0,0)
	if check_newpage((curr_height - h),canvas):
		curr_height = PDF_HEIGHT-margin

	canvas.drawString(margin,curr_height+2, "Table 3 - Character Dynamics")
	canvas.drawString(margin+w+w/2,curr_height+2, "Plot Dynamics")

	curr_height -= h
	table3.wrapOn(canvas, margin,curr_height)
	table3.drawOn(canvas, margin,curr_height)
	table4.wrapOn(canvas, margin+w+w/2,curr_height)
	table4.drawOn(canvas, margin+w+w/2,curr_height)
	curr_height -= VERT_PADDING

	# ============== TABLE 5
	THROUGH_HEADERS = [' ','Class','Concern','Issue','Problem']
	ACT_HEADERS = [' ','Act I','Act II','Act III','Act IV']
	VERT_HEADINGS = ['Overall Story','Main Character','Impact Character','Subjective Story']

	through_data = []
	through_data.append(THROUGH_HEADERS)

	for i, row in enumerate(chunk(in_data['throughlines'],4)):
		row.insert(0, VERT_HEADINGS[i])
		through_data.append(row)


	row = ['Crucial Element', in_data['throughlines'][7]]
	through_data.append(row)

	table5 = through_table(through_data)
	w,h = table5.wrap(0,0)
	if check_newpage((curr_height - h),canvas):
		curr_height = PDF_HEIGHT-margin

	canvas.drawString(margin,curr_height+2, "Table 4 - Throughlines")
	curr_height -= h	
	table5.wrapOn(canvas, margin,curr_height)
	table5.drawOn(canvas, margin,curr_height)
	curr_height -= VERT_PADDING

	# ============== TABLE 6
	table6 = vert_table(abstract_headings[0:4], in_data['abstracts'][0:4],4)
	table7 = vert_table(abstract_headings[4:8], in_data['abstracts'][4:8],4)

	w,h = table6.wrap(0,0)
	if check_newpage((curr_height - h),canvas):
		curr_height = PDF_HEIGHT-margin

	canvas.drawString(margin,curr_height+2, "Table 5 - Flavour")

	curr_height -= h
	table6.wrapOn(canvas, margin,curr_height)
	table6.drawOn(canvas, margin,curr_height)
	table7.wrapOn(canvas, margin+w,curr_height)
	table7.drawOn(canvas, margin+w,curr_height)
	curr_height -= VERT_PADDING

	# ============== TABLE 7
	act_data = []
	act_data.append(ACT_HEADERS)

	for i, row in enumerate(chunk(in_data['acts'],4)):
		row.insert(0, VERT_HEADINGS[i])
		act_data.append(row)

	table8 = through_table(act_data)
	w,h = table8.wrap(0,0)

	if check_newpage((curr_height - h),canvas):
		curr_height = PDF_HEIGHT-margin

	canvas.drawString(margin,curr_height+2, "Table 6 - Acts")
	curr_height -= h
	table8.wrapOn(canvas, margin,curr_height)
	table8.drawOn(canvas, margin,curr_height)
	curr_height -= VERT_PADDING

	canvas.save()