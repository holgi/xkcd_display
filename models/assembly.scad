use <ikea.scad>
use <display-mount.scad>
use <MCAD/servos.scad>

// from ikea.scad
base_plate_width = 230;
spacer_wall = 16;
inner_width = base_plate_width - 2 * spacer_wall;
base_plate_z_pos = 6.97;
base_plate_height = 2;

mount_height = 22;

//%picture_frame();
%spacer();


%translate([0, 11, 0]) rotate([0,0,90]) alignds420();

// the speech bubble
translate([0, 56, base_plate_z_pos + mount_height]) 
    speech_bubble_mount();
