from lxml import etree
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import ATOM_ElementMaker as ATOM
from pykml.factory import GX_ElementMaker as GX

doc = KML.kml(
  KML.Document(
    KML.name('test_image_georef.kml'),
    KML.Style(
      KML.IconStyle(
        KML.scale('1.3'),
        KML.Icon(
          KML.href('http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png'),
        ),
        KML.hotSpot(  x="20",
  y="2",
  xunits="pixels",
  yunits="pixels",
),
      ),
      id="s_ylw-pushpin_hl",
    ),
    KML.StyleMap(
      KML.Pair(
        KML.key('normal'),
        KML.styleUrl('#s_ylw-pushpin'),
      ),
      KML.Pair(
        KML.key('highlight'),
        KML.styleUrl('#s_ylw-pushpin_hl'),
      ),
      id="m_ylw-pushpin",
    ),
    KML.Style(
      KML.IconStyle(
        KML.scale('1.1'),
        KML.Icon(
          KML.href('http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png'),
        ),
        KML.hotSpot(  x="20",
  y="2",
  xunits="pixels",
  yunits="pixels",
),
      ),
      id="s_ylw-pushpin",
    ),
    KML.Placemark(
      KML.name('Test Mark'),
      KML.description('<img src="test.png"/>'),
      KML.LookAt(
        KML.longitude('125.4212804296416'),
        KML.latitude('7.5261603959899'),
        KML.altitude('0'),
        KML.heading('37.38907927626943'),
        KML.tilt('0'),
        KML.range('121049.2080216223'),
        GX.altitudeMode('relativeToSeaFloor'),
      ),
      KML.styleUrl('#m_ylw-pushpin'),
      KML.Point(
        GX.drawOrder('1'),
        KML.coordinates('125.4212804296416,7.5261603959899,0'),
      ),
    ),
  ),
)
print etree.tostring(etree.ElementTree(doc),pretty_print=True)
