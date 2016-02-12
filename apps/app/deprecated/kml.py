#
#
# Obsolete classes and functions. Moved here for sanity. Not checked if it can run as is. Need to check imports.
#

import os, sys, pprint
from fastkml import kml,styles
from pygeoif import geometry
    
FAKE_DATA = {
 "clusters" : 5, 
 "outlets" :10,
 "activations":50,
 "sellouts": 50,
 "stocks":70
}


class KMLReader:
    def __init__(self, k):
        self._k = k
        self.root = k.features().next()
        
        self.__styles()
        
    def __styles(self):
        if isinstance(self.root, kml.Document):
            self.__styles_dict, self.__stylemap_dict = self.__get_styles()
        
    def __get_styles (self):
        _gs_style_dict = {}
        _gs_stylemap_dict = {}
        for s in self.root.styles():
            if isinstance(s, styles.StyleMap):
                _gs_stylemap_dict[s.id] = { 'normal_url' : s.normal.url, 'highlight_url' : s.highlight.url }				
            elif isinstance(s, styles.Style):
                for i_s in s.styles():
                    if isinstance(i_s, styles.IconStyle):					
                        _ = _gs_style_dict.setdefault(s.id, {})
                        _['icon_href'] = i_s.icon_href
                        
                    # end if
                    if isinstance(i_s, styles.LineStyle):
                        _ = _gs_style_dict.setdefault(s.id, {})
                        _['lineColor'] = i_s.color
                        _['lineWidth'] = i_s.width

                    # end if
                    if isinstance(i_s, styles.PolyStyle):
                        _ = _gs_style_dict.setdefault(s.id, {})
                        _.update({ 'polyColor' : i_s.color, 'polyColorMode' : i_s.colorMode, 'polyFill' : i_s.fill, 'polyOutline' : i_s.outline })
                        # _gs_style_dict[s.id] = { 'color' : i_s.color, 'colorMode' : i_s.colorMode, 'fill' : i_s.fill, 'outline' : i_s.outline }
                        # app.logger.debug("Found poly style: %s", _)
                    #end if
                # end for
            # end if
        return _gs_style_dict, _gs_stylemap_dict
        # end for
    def __get_color(self, p_style_url):
        # app.logger.debug("stylemap_dict: %s", pprint.pformat(p_stylemap_dict))
        _s_map = self.__stylemap_dict.get(p_style_url.strip('#'), '')
        # app.logger.debug("Style Url: %s, %s",p_style_url.strip('#'), _s_map)
        if _s_map:			
            _s = self.__styles_dict.get(_s_map['normal_url'].strip('#'), '')
            # app.logger.debug("Style: %s", _s)
            if _s:
                return _s['polyColor'], _s['lineColor'], _s['lineWidth']
            # end if
        # end if
        return ''
    # end def _get_color

    def __get_icon(self, p_style_url):
        # app.logger.debug("stylemap_dict: %s", pprint.pformat(p_stylemap_dict))
        _s_map = self.__stylemap_dict.get(p_style_url.strip('#'), '')
        # app.logger.debug("Style Url: %s, %s",p_style_url.strip('#'), _s_map)
        if _s_map:			
            _s = self.__styles_dict.get(_s_map['normal_url'].strip('#'), '')
            # app.logger.debug("Style: %s", _s)
            if _s:
                return {'href' : _s['icon_href'] }
            # end if
        # end if
        return ''
    def __get_polygons(self, features, selected_elements = [], recurse = False):
        polygons = []
        for c in features: #placemark
            if isinstance(c, kml.Placemark) and isinstance(c.geometry, geometry.Polygon) :
                style_url = c.styleUrl
                _poly_color, _line_color, _line_width = self.__get_color(style_url)

                if not selected_elements or c.name in selected_elements: 
                    polygons.append({
                        'name' : c.name, 
                        'coords' :c.geometry.exterior.coords, 
                        'description': simplejson.loads(c.description.replace('\n','')) if c.description else FAKE_DATA, 
                        'color': {
                            'polyColor' : _poly_color, 
                            'lineColor' : _line_color, 
                            'lineWidth' : _line_width,
                        }
                    })
                    
            if isinstance(c, kml.Folder) and recurse:
                _p = self.__get_polygons(c, recurse)
                polygons.extend(_p)
        return polygons

    def __get_points(self, features, recurse = False):
        points = []
        for c in features: #placemark

            if isinstance(c, kml.Placemark) and isinstance(c.geometry, geometry.Point) :

                style_url = c.styleUrl
                # _poly_color, _line_color, _line_width = self.__get_color(style_url)
                i = self.__get_icon(style_url)
                points.append({ 'name':c.name, 'coords' : c.geometry.coords, 'icon' : i, 'description' : simplejson.loads(c.description.replace('\n','')) if c.description else FAKE_DATA })
                # polygons.append({'name' : c.name, 'coords' :c.geometry.exterior.coords, 'color': { 'polyColor' : _poly_color, 'lineColor' : _line_color, 'lineWidth' : _line_width} })
            
            if isinstance(c, kml.Folder) and recurse:
                _p = self.__get_points(c, recurse)
                points.extend(_p)
        return points

    def getPoints(self, folder_name = None):
        points = []
        if isinstance(self.root, kml.Document):
            for b in self.root.features(): # folder

                if isinstance(b, kml.Folder) and b.name == folder_name:
                    
                    points = self.__get_points(b.features())               
                    # end for
                # end if
            # end for
        # end if	

        return points

    def getPolygons(self, folder_name = None, selected_elements = []):
        polygons = []
        if isinstance(self.root, kml.Document):
            for b in self.root.features(): # folder
                if isinstance(b, kml.Folder) and b.name == folder_name:
                    polygons = self.__get_polygons(b.features()) if not selected_elements else self.__get_polygons(b.features(), selected_elements)
                    # end for
                # end if
            # end for
        # end if	

        return polygons
    

    
# Utility class for getting Polygon from fastkml.KML objects.
# DEPRECATED use KMLReader instead
class Polygon:	
    #
    # get the KML object from fastkml, and get the Polygons only
    # returns list of dict.
    # dict contents: name, coords, color.

    @staticmethod
    def digest(k):
        # get the color of the style url of style_map from styles
        def _get_color(p_style_url, p_stylemap_dict, p_styles_dict):
            # app.logger.debug("stylemap_dict: %s", pprint.pformat(p_stylemap_dict))
            _s_map = p_stylemap_dict.get(p_style_url.strip('#'), '')
            
            # app.logger.debug("Style Url: %s, %s",p_style_url.strip('#'), _s_map)
            if _s_map:			
                _s = p_styles_dict.get(_s_map['normal_url'].strip('#'), '')
                # app.logger.debug("Style: %s", _s)
                if _s:
                
                    return _s['polyColor'], _s['lineColor'], _s['lineWidth']
                # end if
            # end if
            return ''
        # end def _get_color
        
        
        # return dictionary of styles, and style map
        # style: key = style url
        #	     value = dict of normal_url and highlight_url
        #
        # style_map: key = style url
        #            value: dict of color, colorMode, fill, outline		
        def _get_styles (p_document):
            _gs_style_dict = {}
            _gs_stylemap_dict = {}
            for s in p_document.styles():
                if isinstance(s, styles.StyleMap):
                    _gs_stylemap_dict[s.id] = { 'normal_url' : s.normal.url, 'highlight_url' : s.highlight.url }				
                elif isinstance(s, styles.Style):
                    for i_s in s.styles():
                        if isinstance(i_s, styles.IconStyle):					
                            pass
                        # end if
                        if isinstance(i_s, styles.LineStyle):
                            _ = _gs_style_dict.setdefault(s.id, {})
                            _['lineColor'] = i_s.color
                            _['lineWidth'] = i_s.width

                        # end if
                        if isinstance(i_s, styles.PolyStyle):
                            _ = _gs_style_dict.setdefault(s.id, {})
                            _.update({ 'polyColor' : i_s.color, 'polyColorMode' : i_s.colorMode, 'polyFill' : i_s.fill, 'polyOutline' : i_s.outline })
                            # _gs_style_dict[s.id] = { 'color' : i_s.color, 'colorMode' : i_s.colorMode, 'fill' : i_s.fill, 'outline' : i_s.outline }
                            # app.logger.debug("Found poly style: %s", _)
                        #end if
                    # end for
                # end if
            # end for
            # app.logger.debug("styles_dict: %s", pprint.pformat( _gs_style_dict ))
            # app.logger.debug("stylemap_dict: %s", pprint.pformat(_gs_stylemap_dict))
            
            return _gs_style_dict, _gs_stylemap_dict
        # end def _get_styles
        
        polygons = []
        styles_dict = {}
        stylemap_dict = {}
        
        top_level = k.features()
    
        for a in k.features(): # document
            if isinstance(a, kml.Document):
                styles_dict, stylemap_dict = _get_styles(a)
                for b in a.features(): # folder
                    if isinstance(b, kml.Folder):
                        for c in b.features(): #placemark
                            if isinstance(c, kml.Placemark):
                                style_url = c.styleUrl
                                _poly_color, _line_color, _line_width = _get_color(style_url, stylemap_dict, styles_dict )
                                polygons.append({'name' : c.name, 'coords' :c.geometry.exterior.coords, 'color': { 'polyColor' : _poly_color, 'lineColor' : _line_color, 'lineWidth' : _line_width} })
                            # end if
                        # end for
                    # end if
                # end for
            # end if	
        # end for
        return polygons
