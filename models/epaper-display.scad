epd_length = 91;
epd_width = 77;
epd_height = 1.2;

epd_cable_length = 17;
epd_cable_width = 1;
epd_outer_width = epd_width + epd_cable_width;


module epaper_display(
    length=epd_length, 
    width=epd_width, 
    height=epd_height,
    cable_length = epd_cable_length,
    cable_width = epd_cable_width
 ) {
        
    cable_x_offset = (epd_length - cable_length) / 2;
    cable_y_offset = epd_width;

    cube([length, width, height]);
    translate([cable_x_offset, cable_y_offset-1, 0])
        cube([cable_length, cable_width+2, height]);

    }

function epaper_dimensions(
    length=epd_length, 
    width=epd_width, 
    height=epd_height,
    cable_length = epd_cable_length,
    cable_width = epd_cable_width)
    = [length, width+cable_width, height];



epaper_display();
echo("Standard ePaper Outer Dimensions:", epaper_dimensions());