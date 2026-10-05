"""40 authored compositions, not title substitutions. Coordinates describe content slots."""
def F(key, label, text, font, x,y,w,h): return (key,label,text,font,x,y,w,h)
def D(ornament,x,y,w,h,stroke=1.3,rotation=0):
    return {'ornament':ornament,'x':x,'y':y,'w':w,'h':h,'stroke_width':stroke,'rotation':rotation}
def T(identity,name,occasion,fields,decorations=(),requires='text',effects=None,**extra):
    return {'id':identity,'name':name,'occasion':occasion,'subtitle':occasion,'requires':requires,
            'fields':fields,'decorations':decorations,'effects':effects or {},**extra}

UNIVERSAL = [
 T('monogram','Name oder Monogramm','Namen & Initialen',[
   F('initials','Initialen oder Name','M','cinzel',.08,.17,.84,.38),F('tagline','Zusatzzeile','Dein Unikat','montserrat',.10,.63,.80,.12)]),
 T('wedding','Hochzeit','Hochzeit & Liebe',[
   F('names','Zwei Namen','Anna & Ben','great-vibes',.04,.16,.92,.29),F('date','Datum','14.06.2026','lora',.15,.51,.70,.12),F('dedication','Widmung (optional)','Für immer','montserrat',.10,.73,.80,.10)]),
 T('birthday','Geburtstag oder Jubiläum','Geburt & Jubiläum',[
   F('name','Name','Mia','dancing-script',.12,.08,.76,.17),F('number','Zahl','30','bebas-neue',.12,.32,.76,.34),F('message','Kurze Botschaft','Alles Liebe','open-sans',.08,.78,.84,.10)]),
 T('photo','Fotogeschenk','Foto & Erinnerung',[
   F('photo','Bild ersetzen',None,None,.14,.06,.72,.56),F('caption','Bildunterschrift','Unser Moment','lora',.08,.72,.84,.15)],requires='photo'),
 T('company','Firma oder Verein','Firma & Verein',[
   F('logo','Logo ersetzen',None,None,.22,.05,.56,.42),F('company','Name','Dein Verein','oswald',.08,.55,.84,.17),F('tagline','Zusatzzeile','Gemeinsam mehr','open-sans',.08,.81,.84,.09)],requires='logo'),
 T('dedication','Schlichte Widmung','Danke & Widmung',[
   F('message','Persönliche Botschaft','Für dich','cormorant-garamond',.07,.26,.86,.24),F('signature','Absender oder Datum','Von Herzen','caveat',.16,.64,.68,.13)]),
 T('double-frame','Doppelrahmen','Namen & Initialen',[
   F('name','Name','LENA','raleway',.18,.30,.64,.23),F('date','Jahr oder Datum','EST. 2026','roboto-mono',.23,.64,.54,.1)],
   [D('double-rect',.03,.08,.94,.84),D('line',.32,.57,.36,.025)]),
 T('laurel-award','Lorbeer-Auszeichnung','Sport & Auszeichnung',[
   F('number','Platzierung','1','cinzel',.32,.2,.36,.35),F('title','Auszeichnung','CHAMPION','montserrat',.18,.59,.64,.13),F('year','Jahr','2026','lora',.36,.79,.28,.08)],
   [D('laurel',.015,.015,.97,.97)]),
 T('heart-greeting','Herzgruß','Hochzeit & Liebe',[
   F('message','Herzensbotschaft','Du & ich','allura',.2,.33,.6,.23),F('signature','Zusatz','Für immer','nunito',.26,.69,.48,.09)],
   [D('heart',.06,.03,.88,.84),D('branch',.26,.84,.48,.1)]),
 T('circle-message','Kreis-Botschaft','Danke & Widmung',[
   F('message','Botschaft','DU BIST GOLD','montserrat',.16,.18,.68,.18),F('name','Name','Mia','dancing-script',.25,.42,.5,.22),F('date','Datum','2026','space-mono',.33,.74,.34,.09)],
   [D('circle-frame',.025,.025,.95,.95)],effects={'message':{'curvature':55}}),
]

WOOD = [
 T('wood-family','Familienkranz','Familie & Zuhause',[
   F('heading','Überschrift','FAMILIE','montserrat',.24,.26,.52,.09),F('name','Familienname','Bergmann','great-vibes',.15,.42,.7,.2),F('year','Seit wann','SEIT 2020','lora',.29,.69,.42,.08)],
   [D('wreath',.01,.01,.98,.98)]),
 T('wood-rustic','Rustikales Namensschild','Familie & Zuhause',[
   F('name','Name','WILLKOMMEN','special-elite',.16,.36,.68,.18),F('family','Familie','BEI DEN BERGS','amatic-sc',.2,.70,.6,.16)],
   [D('ribbon',.03,.26,.94,.37),D('branch',.22,.05,.56,.15)]),
 T('wood-wedding','Hochzeitskranz','Hochzeit & Liebe',[
   F('names','Zwei Namen','Anna & Ben','allura',.15,.35,.7,.2),F('date','Hochzeitsdatum','14.06.2026','cormorant-garamond',.25,.63,.5,.1)],
   [D('floral',.02,.02,.96,.96),D('heart',.44,.17,.12,.11)]),
 T('wood-anniversary','Jubiläums-Baumscheibe','Geburt & Jubiläum',[
   F('years','Jahre','25','playfair-display',.26,.26,.48,.28),F('names','Namen','Eva & Paul','dancing-script',.2,.58,.6,.16),F('caption','Zusatz','GEMEINSAME JAHRE','montserrat',.24,.75,.52,.07)],
   [D('double-circle',.02,.02,.96,.96),D('sparkles',.3,.09,.4,.11)],effects={'years':{'text_mode':'outline','outline_width':.9}}),
 T('wood-birth','Geburtsandenken','Geburt & Jubiläum',[
   F('name','Vorname','Emilia','dancing-script',.07,.21,.86,.21),F('date','Geburtsdatum','08.03.2026','lora',.12,.54,.76,.11),F('details','Gewicht oder Größe','3200 g · 50 cm','nunito',.09,.77,.82,.1)],
   [D('star',.05,.04,.13,.13),D('star',.82,.1,.1,.1),D('diamond-divider',.2,.67,.6,.035)]),
 T('wood-baptism','Taufgeschenk','Geburt & Jubiläum',[
   F('title','Anlass','ZUR TAUFE','cinzel',.13,.05,.74,.1),F('name','Name','Noah','allura',.15,.32,.7,.24),F('message','Segenswunsch','Behütet auf allen Wegen','lora',.06,.62,.88,.11),F('date','Datum','24.05.2026','open-sans',.27,.85,.46,.07)],
   [D('branch',.18,.17,.64,.12),D('line',.3,.77,.4,.02)]),
 T('wood-floral','Blumenmonogramm','Namen & Initialen',[
   F('initial','Initiale','L','cormorant-garamond',.24,.22,.52,.44),F('name','Vorname','Luisa','kalam',.3,.72,.4,.12)],
   [D('floral',.01,.01,.98,.98)]),
 T('wood-mountains','Wald- und Bergmotiv','Natur & Reisen',[
   F('title','Botschaft','DRAUSSEN ZUHAUSE','oswald',.02,.52,.96,.15),F('name','Name oder Ort','Die Bergmenschen','caveat',.12,.81,.76,.13)],
   [D('mountains',.05,.02,.64,.36),D('forest',.7,.16,.23,.25),D('line',.13,.74,.74,.018)]),
 T('wood-kitchen','Küchenbrett','Küche & Garten',[
   F('name','Name','OMAS','bebas-neue',.12,.19,.76,.24),F('title','Lieblingsort','Lieblingsküche','lobster',.04,.45,.92,.2),F('message','Zusatz','MIT LIEBE GEKOCHT','montserrat',.08,.8,.84,.075)],
   [D('branch',.18,.025,.64,.12),D('diamond-divider',.15,.71,.7,.04)]),
 T('wood-bbq','Grillmeister','Küche & Garten',[
   F('name','Name','TOM','anton',.17,.27,.66,.24),F('title','Titel','GRILLMEISTER','oswald',.14,.62,.72,.14),F('year','Jahr','SEIT 1988','roboto-mono',.29,.84,.42,.07)],
   [D('star',.41,.065,.18,.16),D('ribbon',.015,.52,.97,.32)],effects={'name':{'shadow_enabled':True,'shadow_distance':1.5}}),
 T('wood-garden','Gartenliebe','Küche & Garten',[
   F('name','Name','Lenas Garten','kalam',.20,.25,.74,.20),F('message','Gartenspruch','Hier wächst Glück','lora',.22,.58,.7,.12)],
   [D('branch',.045,.06,.11,.83,rotation=-90),D('branch',.26,.79,.66,.15),D('heart',.71,.035,.13,.13)]),
 T('wood-pet','Haustier-Erinnerung','Tiere & Erinnerung',[
   F('photo','Erinnerungsfoto',None,None,.18,.09,.43,.41),F('name','Name','Luna','great-vibes',.12,.61,.76,.2),F('date','Erinnerungszeile','Für immer im Herzen','lora',.1,.86,.8,.08)],
   [D('paw',.69,.19,.23,.24),D('corner-marks',.14,.05,.51,.49)],requires='photo'),
 T('wood-home','Haussegen','Familie & Zuhause',[
   F('heading','Überschrift','UNSER ZUHAUSE','cinzel',.15,.23,.7,.12),F('message','Haussegen','Hier wohnt das Glück','caveat',.12,.45,.76,.16),F('family','Familie','Familie Berg','lora',.22,.72,.56,.1)],
   [D('rect-frame',.04,.035,.92,.93),D('heart',.44,.06,.12,.11),D('branch',.32,.85,.36,.09)]),
 T('wood-teacher','Danke-Geschenk für Lehrkräfte','Danke & Widmung',[
   F('thanks','Dank','Danke!','permanent-marker',.05,.14,.9,.24),F('name','Name','Frau Müller','lora',.08,.44,.84,.14),F('class','Klasse oder Gruppe','DEINE KLASSE 4A','montserrat',.06,.74,.88,.1)],
   [D('line',.08,.65,.84,.02),D('sparkles',.36,.88,.28,.08)]),
 T('wood-friendship','Freundschaft','Hochzeit & Liebe',[
   F('first','Erster Name','Lena','dancing-script',.03,.12,.55,.19),F('second','Zweiter Name','Mia','dancing-script',.43,.35,.54,.21),F('message','Botschaft','Zusammen ist alles schöner','caveat',.02,.79,.96,.12)],
   [D('heart',.43,.2,.12,.13),D('branch',.06,.57,.88,.14)]),
 T('wood-christmas','Weihnachtsanhänger','Weihnachten',[
   F('name','Name','Mia','allura',.24,.34,.52,.22),F('message','Gruß','FROHES FEST','amatic-sc',.18,.65,.64,.14),F('year','Jahr','2026','lora',.36,.84,.28,.07)],
   [D('circle-frame',.02,.02,.96,.96),D('star',.4,.08,.2,.19)]),
]

METAL = [
 T('metal-monogram','Technisches Monogramm','Namen & Initialen',[
   F('initials','Initialen','MB','space-mono',.2,.2,.6,.37),F('year','Kennzeichnung','ED. 01','roboto-mono',.27,.72,.46,.09)],
   [D('corner-marks',.02,.03,.96,.94),D('line',.27,.63,.46,.022)],effects={'initials':{'text_mode':'outline','outline_width':.9}}),
 T('metal-industrial','Industrielles Namensschild','Beschriftung & Technik',[
   F('name','Name','M. BAYER','anton',.12,.19,.76,.26),F('role','Bereich','WERKSTATT','roboto-mono',.14,.63,.72,.12)],
   [D('double-rect',.02,.05,.96,.89),D('line',.1,.53,.8,.028)]),
 T('metal-coordinates','Koordinatenplakette','Natur & Reisen',[
   F('latitude','Breitengrad','51.2642 N','roboto-mono',.06,.12,.88,.2),F('longitude','Längengrad','6.5481 E','roboto-mono',.06,.4,.88,.2),F('place','Ort','UNSER ORT','montserrat',.19,.81,.62,.1)],
   [D('diamond-divider',.12,.69,.76,.05)]),
 T('metal-keyring','Initialen-Schlüsselanhänger','Namen & Initialen',[
   F('initials','Initialen','LK','bebas-neue',.25,.18,.5,.44),F('date','Datum','14·06·26','space-mono',.2,.75,.6,.09)],
   [D('circle-frame',.03,.03,.94,.94)],effects={'initials':{'shadow_enabled':True,'shadow_distance':1.3,'shadow_angle':0}}),
 T('metal-pet','Haustiermarke','Tiere & Erinnerung',[
   F('name','Name','LUNA','nunito',.12,.4,.76,.23),F('phone','Telefonnummer','0123 456789','roboto-mono',.08,.82,.84,.09)],
   [D('paw',.34,.045,.32,.28),D('line',.17,.72,.66,.022)]),
 T('metal-club','Vereinsabzeichen','Firma & Verein',[
   F('initials','Vereinskürzel','SV','oswald',.28,.25,.44,.27),F('club','Vereinsname','TEAM NORD','montserrat',.16,.58,.68,.12),F('year','Gründungsjahr','1920','roboto-mono',.35,.79,.3,.08)],
   [D('laurel',.01,.01,.98,.98)]),
 T('metal-badge','Firmenbadge','Firma & Verein',[
   F('logo','Firmenlogo',None,None,.07,.21,.31,.44),F('company','Firma','ACME','oswald',.45,.23,.48,.19),F('role','Bereich','DESIGN','open-sans',.45,.54,.48,.1)],
   [D('rect-frame',.015,.08,.97,.76),D('line',.1,.92,.8,.022)],requires='logo',wide=True),
 T('metal-tool','Werkzeugkennzeichnung','Beschriftung & Technik',[
   F('code','Werkzeugnummer','WZ-042','roboto-mono',.06,.13,.88,.22),F('owner','Eigentümer','M. BAYER','montserrat',.07,.49,.86,.13),F('location','Standort','WERKSTATT 01','space-mono',.08,.8,.84,.1)],
   [D('line',.02,.4,.96,.026),D('corner-marks',.02,.69,.96,.28)]),
 T('metal-sport','Sportauszeichnung','Sport & Auszeichnung',[
   F('place','Platz','1','anton',.27,.17,.46,.35),F('sport','Disziplin','10 KM LAUF','oswald',.12,.63,.76,.13),F('year','Jahr','2026','montserrat',.34,.85,.32,.07)],
   [D('star',.06,.29,.16,.16),D('star',.78,.29,.16,.16),D('diamond-divider',.19,.55,.62,.03)]),
 T('metal-vehicle','Fahrzeugplakette','Beschriftung & Technik',[
   F('model','Modell','CLASSIC 911','bebas-neue',.07,.13,.86,.21),F('year','Baujahr','1984','space-mono',.24,.41,.52,.23),F('serial','Seriennummer','NO. 0086','roboto-mono',.2,.79,.6,.09)],
   [D('rect-frame',.02,.025,.96,.95),D('line',.13,.72,.74,.024)]),
 T('metal-travel','Reiseanhänger','Natur & Reisen',[
   F('name','Name','LENA BERG','montserrat',.04,.53,.92,.17),F('contact','Kontakt','0123 456789','space-mono',.08,.84,.84,.09)],
   [D('mountains',.08,.035,.84,.36),D('line',.04,.75,.92,.025)]),
 T('metal-wedding','Modernes Hochzeitsschild','Hochzeit & Liebe',[
   F('first','Erster Name','ANNA','raleway',.1,.09,.8,.18),F('second','Zweiter Name','BEN','raleway',.1,.55,.8,.18),F('date','Datum','14.06.2026','roboto-mono',.17,.86,.66,.08)],
   [D('diamond-divider',.09,.36,.82,.085)]),
 T('metal-dedication','Klare Widmung','Danke & Widmung',[
   F('message','Widmung','FÜR DEINEN WEG','montserrat',.04,.30,.92,.17),F('signature','Absender','Von Papa','lora',.29,.65,.66,.11)],
   [D('line',.055,.08,.018,.82),D('star',.84,.12,.11,.1)]),
 T('metal-number','Nummern- und Datumsschild','Beschriftung & Technik',[
   F('number','Nummer','No. 042','space-mono',.1,.13,.8,.27),F('date','Datum','06 / 2026','roboto-mono',.17,.64,.66,.15)],
   [D('corner-marks',.02,.035,.96,.93),D('line',.08,.5,.84,.028)]),
]

TEMPLATES = [dict(t,collection=collection) for collection,items in [('holz',WOOD),('metall',METAL),('universell',UNIVERSAL)] for t in items]
BY_ID = {t['id']:t for t in TEMPLATES}