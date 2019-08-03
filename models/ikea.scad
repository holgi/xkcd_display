base_plate_width = 230;
base_plate_height = 2;

spacer_wall = 16;
spacer_height = 28;

inner_height = 38;

outer_frame_height = 40;
outer_frame_wall = 30;
outer_frame_viewport = 224;

glass_height = 1;

gap = 1;

do_not_touch = 0.01;



outer_frame_inside_width = base_plate_width + 2 * (gap + do_not_touch);
outer_frame_outside_width = outer_frame_inside_width + 2 * outer_frame_wall;
outer_frame_inside_height = outer_frame_height - inner_height;

glass_z_pos = inner_height - glass_height - do_not_touch;

spacer_z_pos = glass_z_pos - spacer_height - do_not_touch;
spacer_inner_width = base_plate_width - 2 * spacer_wall;

base_plate_z_pos = spacer_z_pos - base_plate_height - do_not_touch;

module outer_frame() {
    difference(){
        translate([-outer_frame_outside_width/2, -outer_frame_outside_width/2, 0]) {
            cube([outer_frame_outside_width, outer_frame_outside_width, outer_frame_height]);
        }
        translate([-outer_frame_inside_width/2, -outer_frame_inside_width/2, -1]) {
            cube([outer_frame_inside_width, outer_frame_inside_width, inner_height+1]);
        }
        translate([-outer_frame_viewport/2, -outer_frame_viewport/2, -1]) {
            cube([outer_frame_viewport, outer_frame_viewport, outer_frame_height+2]);
        }
    }
}

module spacer() {
    difference() {
        translate([-base_plate_width/2, -base_plate_width/2, spacer_z_pos]) cube([base_plate_width, base_plate_width, spacer_height]);
        translate([-spacer_inner_width/2, -spacer_inner_width/2, spacer_z_pos-1]) cube([spacer_inner_width, spacer_inner_width, spacer_height+2]);
    }
}


module glass() {
    color([.9,.9,1]) translate([-base_plate_width/2, -base_plate_width/2, glass_z_pos]) cube([base_plate_width, base_plate_width, glass_height]);
}

module picture_frame() {
    outer_frame();
    spacer();
    glass();

}


module base_plate() {

    translate([-base_plate_width/2, -base_plate_width/2, base_plate_z_pos]) cube([base_plate_width, base_plate_width, base_plate_height]);
}


union() {
    %picture_frame();

    // base plate
    #base_plate();
}
