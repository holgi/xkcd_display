use <epaper-display.scad>
use <pillars.scad>
use <servo-mount.scad>

bubble_height = 2;
epd_frame_width=7;
epd_frame_support=3;
epd_frame_height=2;
epd_back_wall_widht = 2;
pillar_width=15;
pillar_height=22;

epd_cutout_surcharge = 1;

// get the default outer epaper dimensions
ep_outer_dimensions = epaper_dimensions();
ep_length = ep_outer_dimensions[0] + epd_cutout_surcharge;
ep_width = ep_outer_dimensions[1] + epd_cutout_surcharge;
ep_height = ep_outer_dimensions[2];
ep_cable_length = ep_outer_dimensions[3];

// ep_y_offset value determined manually
ep_y_offset = -37;

// support plate calculation
epd_frame_overlay = epd_frame_width - epd_frame_support;

plate_length = ep_length + 2 * epd_frame_overlay;
plate_width = ep_width + 2 * epd_frame_overlay;
plate_height = epd_frame_height + bubble_height;
plate_cutout_lengt = plate_length - 2 * epd_frame_width;
plate_cutout_width = plate_width - 2 * epd_frame_width;


module speech_bubble_base(bubble_height=bubble_height) {
    difference() {
        // base elipsoid form
        translate([0, 0, 0]) scale([1.4,1,1]) 
            cylinder(h=bubble_height, r=54, $fa=1);
        // wiper hole
        translate([0 , -45, -1]) 
            cylinder(h=bubble_height + 2, r=5, $fa=1);
    }
}

module epaper_support_plate() {
    
    x_offset = -plate_length / 2;
    y_offset = ep_y_offset - epd_cutout_surcharge - epd_frame_overlay;
    z_offset = bubble_height - plate_height;
    
    intersection() {
        // the base support plate
        translate([x_offset, y_offset, z_offset])
            cube([plate_length, plate_width, plate_height]);
        // cut the edges of the plate in shape with the bubble
        translate([0, 0, -1]) speech_bubble_base(bubble_height=plate_height+2);
    }
}

module epaper_bubble_with_support_plate() {
    speech_bubble_base();
    epaper_support_plate();
}

module epaper_bubble_support_frame() {

    x_offset = -plate_length / 2;
    y_offset = ep_y_offset - epd_cutout_surcharge - epd_frame_overlay;
    z_offset = bubble_height - plate_height;

    difference() {
        // combine the speech bubble with the base support plate
        epaper_bubble_with_support_plate();
        // remove the inner support frame cutout
        translate([x_offset+epd_frame_width, y_offset+epd_frame_width, z_offset - 1])
            cube([plate_cutout_lengt, plate_cutout_width, plate_height + 2]);
        // make a little space for the servo
        // should be asymetric
        translate([-9, y_offset-epd_frame_width/2, -10]) cube([15,epd_frame_width*2,10]);
        translate([-9, ep_y_offset-epd_cutout_surcharge, -5])
            cube([15,epd_frame_overlay+1,10]);
    }
}

module support_pillars() {
    
    z_offset = bubble_height - pillar_height;
    y_offset_wall = -ep_y_offset - pillar_width + epd_cutout_surcharge;
    y_offset_servo = ep_y_offset;
    x_offset = ep_length / 2 - epd_cutout_surcharge;
    
    translate([-x_offset, y_offset_wall, z_offset])
        z_pillar(width=pillar_width, height=pillar_height);
    translate([x_offset, y_offset_wall+pillar_width, z_offset])
        rotate([0, 0, 180])
            z_pillar(width=pillar_width, height=pillar_height);
    translate([x_offset-4, y_offset_servo, z_offset])
        rotate([0, 0, 90])
            z_pillar(width=pillar_width, height=pillar_height);
    translate([-x_offset+4+pillar_width, y_offset_servo, z_offset])
        rotate([0, 0, 90])
            z_pillar(width=pillar_width, height=pillar_height);
    }

module support_base_with_pillars() {
    epaper_bubble_support_frame();
    support_pillars();
}


module speech_bubble_cut() {
    
    ep_z_offset = bubble_height - ep_height;
    ep_y_offset = ep_y_offset - epd_cutout_surcharge;
    
    difference()  {
        support_base_with_pillars();
        // cutout for epaper
        // the + .01 on y_offset is just to remove an artefact
        translate([-ep_length/2, ep_y_offset + .01, ep_z_offset]) 
            epaper_display(length=ep_length, width=ep_width, height=ep_height+1); 
        // cut frame wall
        translate([-ep_length/2-1, ep_y_offset + ep_width + epd_back_wall_widht, -2])
            cube([ep_length+2, ep_width, bubble_height+4]);
        // cut for cable
        translate([-ep_cable_length/2-1, ep_y_offset + ep_width, -2])
            cube([ep_cable_length+2, epd_back_wall_widht+1, bubble_height+4]);
    }
}

module speech_bubble_mount() {
    speech_bubble_cut();
    translate([0 , -45, bubble_height]) aligned_support_mount(false);
}

speech_bubble_mount();