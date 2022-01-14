MODULE Module1
    ! Description:        !
    !   Cuboid Parameters !
    ! Center Position
    LOCAL CONST num CENTER_POSITION{3} := [450.0,0.0,500.0];
    ! Size
    LOCAL CONST num CUBOID_SIZE{3} := [360.0,360.0,360.0];
    ! Vertices
    LOCAL CONST num C00{3} := [(CENTER_POSITION{1} - CUBOID_SIZE{1}/2) + CUBOID_SIZE{1},(CENTER_POSITION{2} - CUBOID_SIZE{2}/2)                 ,(CENTER_POSITION{3} - CUBOID_SIZE{3}/2)];
    LOCAL CONST num C01{3} := [(CENTER_POSITION{1} - CUBOID_SIZE{1}/2) + CUBOID_SIZE{1},(CENTER_POSITION{2} - CUBOID_SIZE{2}/2) + CUBOID_SIZE{2},(CENTER_POSITION{3} - CUBOID_SIZE{3}/2)];
    LOCAL CONST num C02{3} := [(CENTER_POSITION{1} - CUBOID_SIZE{1}/2)                 ,(CENTER_POSITION{2} - CUBOID_SIZE{2}/2) + CUBOID_SIZE{2},(CENTER_POSITION{3} - CUBOID_SIZE{3}/2)];
    LOCAL CONST num C03{3} := [(CENTER_POSITION{1} - CUBOID_SIZE{1}/2)                 ,(CENTER_POSITION{2} - CUBOID_SIZE{2}/2)                 ,(CENTER_POSITION{3} - CUBOID_SIZE{3}/2)];
    LOCAL CONST num C10{3} := [(CENTER_POSITION{1} - CUBOID_SIZE{1}/2) + CUBOID_SIZE{1},(CENTER_POSITION{2} - CUBOID_SIZE{2}/2)                 ,(CENTER_POSITION{3} - CUBOID_SIZE{3}/2) + CUBOID_SIZE{3}];
    LOCAL CONST num C11{3} := [(CENTER_POSITION{1} - CUBOID_SIZE{1}/2) + CUBOID_SIZE{1},(CENTER_POSITION{2} - CUBOID_SIZE{2}/2) + CUBOID_SIZE{2},(CENTER_POSITION{3} - CUBOID_SIZE{3}/2) + CUBOID_SIZE{3}];
    LOCAL CONST num C12{3} := [(CENTER_POSITION{1} - CUBOID_SIZE{1}/2)                 ,(CENTER_POSITION{2} - CUBOID_SIZE{2}/2) + CUBOID_SIZE{2},(CENTER_POSITION{3} - CUBOID_SIZE{3}/2) + CUBOID_SIZE{3}];
    LOCAL CONST num C13{3} := [(CENTER_POSITION{1} - CUBOID_SIZE{1}/2)                 ,(CENTER_POSITION{2} - CUBOID_SIZE{2}/2)                 ,(CENTER_POSITION{3} - CUBOID_SIZE{3}/2) + CUBOID_SIZE{3}];
    LOCAL CONST num CUBOID_VERTICES{8,3} := [[C00{1}, C00{2}, C00{3}], 
                                             [C01{1}, C01{2}, C01{3}],
                                             [C02{1}, C02{2}, C02{3}],
                                             [C03{1}, C03{2}, C03{3}],
                                             [C10{1}, C10{2}, C10{3}],
                                             [C11{1}, C11{2}, C11{3}],
                                             [C12{1}, C12{2}, C12{3}],
                                             [C13{1}, C13{2}, C13{3}]];
                                       
    ! Initialization Position (Auxiliary Target)
    VAR robtarget Target_Auxiliary:=[[CENTER_POSITION{1}, CENTER_POSITION{2}, CENTER_POSITION{3}],[-0.000000007,0,1,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    ! Identifier for the EGM correction
    LOCAL VAR egmident egm_id;
    ! EGM pose frames
    LOCAL CONST pose egm_correction_frame := [[0.0, 0.0, 0.0],[1.0, 0.0, 0.0, 0.0]];
    LOCAL CONST pose egm_sensor_frame     := [[0.0, 0.0, 0.0],[1.0, 0.0, 0.0, 0.0]];
    ! The work object. Base Frame
    LOCAL PERS wobjdata egm_wobj := [FALSE, TRUE, "", [[0.0, 0.0, 0.0],[1.0, 0.0, 0.0, 0.0]], [[0.0, 0.0, 0.0],[1.0, 0.0, 0.0, 0.0]]];
    ! Limits for convergence
    ! Cartesian: +- 0.1 mm
    LOCAL CONST egm_minmax egm_condition_cartesian := [-0.1, 0.1];
    ! Orientation: +- 0.1 degrees
    LOCAL CONST egm_minmax egm_condition_orient := [-0.1, 0.1];
    
    PROC main()
        ! Move to the starting position
        MoveL Target_Auxiliary,v100,fine,tool0\WObj:=wobj0;
        
        ! Call Procedure -> Testing the workspace of the robot from the created cube
        !Test_Cuboid_Workspace;
        
        ! Call Procedure -> Cartesian Move Procedure (EGM)
        !EGM_CARTESIAN_MOVE;
    ENDPROC
    
    PROC EGM_CARTESIAN_MOVE()
        ! Description:                                       !
        ! Externally Guided motion (EGM) - Cartesian Control !
    
        ! Register an EGM id
        EGMGetId egm_id;
            
        ! Setup the EGM communication
        EGMSetupUC ROB_1, egm_id, "default", "ROB_1", \Pose; 
            
        ! EGM While {Cartesian}
        WHILE TRUE DO
            ! Prepare for an EGM communication session
            EGMActPose egm_id, 
                       \WObj:=egm_wobj,
                       egm_correction_frame,
                       EGM_FRAME_BASE,
                       egm_sensor_frame,
                       EGM_FRAME_BASE
                       \X:=egm_condition_cartesian
                       \Y:=egm_condition_cartesian
                       \Z:=egm_condition_cartesian
                       \Rx:=egm_condition_orient
                       \Ry:=egm_condition_orient
                       \Rz:=egm_condition_orient
                       \LpFilter:=100
                       \SampleRate:=4
                       \MaxPosDeviation:=1000
                       \MaxSpeedDeviation:=50;
                        
            ! Start the EGM communication session
            EGMRunPose egm_id, EGM_STOP_RAMP_DOWN, \X \Y \Z \Rx \Ry \Rz \CondTime:=1000 \RampInTime:=0.5 \RampOutTime:=0.5 \PosCorrGain:=1.0;
            
            ! Release the EGM id
            !EGMReset egm_id;
            
            ! Wait 2 seconds {No data from EGM sensor}
            !WaitTime 2;
        ENDWHILE
        
        ERROR
        IF ERRNO = ERR_UDPUC_COMM THEN
            TPWrite "Communication timedout";
            TRYNEXT;
        ENDIF
    ENDPROC
    
    PROC Test_Cuboid_Workspace()
        ! Move to the starting position
        MoveL Target_Auxiliary,v100,fine,tool0\WObj:=wobj0;
        FOR i FROM 1 TO 8 DO
            ! Testing the workspace of the robot from the created cube
            MoveL Offs(Target_Auxiliary,
                       CUBOID_VERTICES{i, 1} - CENTER_POSITION{1}, 
                       CUBOID_VERTICES{i, 2} - CENTER_POSITION{2},
                       CUBOID_VERTICES{i, 3} - CENTER_POSITION{3}), 
                       v100,fine,tool0\WObj:=wobj0;
        ENDFOR
    ENDPROC
ENDMODULE