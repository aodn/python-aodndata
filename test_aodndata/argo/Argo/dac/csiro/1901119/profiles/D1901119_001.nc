CDF   	   
      N_PROF        N_LEVELS   F   N_CALIB       STRING2       STRING4       STRING8       STRING16      STRING32       STRING64   @   	STRING256         	DATE_TIME         N_PARAM       	N_HISTORY                title         Argo float vertical profile    institution       CSIRO      source        
Argo float     history       q2013-07-27T12:59:35Z creation;2014-08-15T15:22:01Z update;2014-10-06T03:01:40Z update;2014-10-20T00:27:00Z update      
references        (http://www.argodatamgt.org/Documentation   user_manual_version       3.1    Conventions       Argo-3.1 CF-1.6    featureType       trajectoryProfile         @   	DATA_TYPE                  	long_name         	Data type      conventions       Argo reference table 1     
_FillValue                    6�   FORMAT_VERSION                 	long_name         File format version    
_FillValue                    6�   HANDBOOK_VERSION               	long_name         Data handbook version      
_FillValue                    6�   REFERENCE_DATE_TIME       
         	long_name         !Date of reference for Julian days      conventions       YYYYMMDDHHMISS     
_FillValue                    6�   DATE_CREATION         
         	long_name         Date of file creation      conventions       YYYYMMDDHHMISS     
_FillValue                    6�   DATE_UPDATE       
         	long_name         Date of update of this file    conventions       YYYYMMDDHHMISS     
_FillValue                    7   PLATFORM_NUMBER                    	long_name         Float unique identifier    conventions       WMO float identifier : A9IIIII     
_FillValue                    7   PROJECT_NAME                   	long_name         Name of the project    
_FillValue                  @  7   PI_NAME                    	long_name         "Name of the principal investigator     
_FillValue                  @  7\   STATION_PARAMETERS                        conventions       Argo reference table 3     	long_name         ,List of available parameters for the station   
_FillValue                  0  7�   CYCLE_NUMBER                	long_name         Float cycle number     
_FillValue         ��   conventions       =0...N, 0 : launch cycle (if exists), 1 : first complete cycle           7�   	DIRECTION                   	long_name         !Direction of the station profiles      conventions       -A: ascending profiles, D: descending profiles      
_FillValue                    7�   DATA_CENTRE                    	long_name         .Data centre in charge of float data processing     conventions       Argo reference table 4     
_FillValue                    7�   DC_REFERENCE                   	long_name         (Station unique identifier in data centre   conventions       Data centre convention     
_FillValue                     7�   DATA_STATE_INDICATOR                   	long_name         1Degree of processing the data have passed through      conventions       Argo reference table 6     
_FillValue                    7�   	DATA_MODE                   	long_name         Delayed mode or real time data     conventions       >R : real time; D : delayed mode; A : real time with adjustment     
_FillValue                    7�   PLATFORM_TYPE                      	long_name         Type of float      conventions       Argo reference table 23    
_FillValue                     8    FLOAT_SERIAL_NO                    	long_name         Serial number of the float     
_FillValue                     8    FIRMWARE_VERSION                   	long_name         Instrument firmware version    
_FillValue                     8@   WMO_INST_TYPE                      	long_name         Coded instrument type      conventions       Argo reference table 8     
_FillValue                    8`   JULD                standard_name         time   	long_name         ?Julian day (UTC) of the station relative to REFERENCE_DATE_TIME    conventions       8Relative julian days with decimal part (as parts of day)   units         "days since 1950-01-01 00:00:00 UTC     
resolution        >�����h�   
_FillValue        A.�~       axis      T           8d   JULD_QC                 	long_name         Quality on date and time   conventions       Argo reference table 2     
_FillValue                    8l   JULD_LOCATION                   	long_name         @Julian day (UTC) of the location relative to REFERENCE_DATE_TIME   units         "days since 1950-01-01 00:00:00 UTC     conventions       8Relative julian days with decimal part (as parts of day)   
resolution        >�����h�   
_FillValue        A.�~       axis      T           8p   LATITUDE                	long_name         &Latitude of the station, best estimate     standard_name         latitude   units         degree_north   	valid_min         �V�        	valid_max         @V�        axis      Y      
_FillValue        @�i�            8x   	LONGITUDE                   	long_name         'Longitude of the station, best estimate    standard_name         	longitude      units         degree_east    	valid_min         �f�        	valid_max         @f�        axis      X      
_FillValue        @�i�            8�   POSITION_QC                 	long_name         ,Quality on position (latitude and longitude)   conventions       Argo reference table 2     
_FillValue                    8�   POSITIONING_SYSTEM                     	long_name         Positioning system     
_FillValue                    8�   PROFILE_PRES_QC                 	long_name         #Global quality flag of PRES profile    conventions       Argo reference table 2a    
_FillValue                    8�   PROFILE_TEMP_QC                 	long_name         #Global quality flag of TEMP profile    conventions       Argo reference table 2a    
_FillValue                    8�   PROFILE_PSAL_QC                 	long_name         #Global quality flag of PSAL profile    conventions       Argo reference table 2a    
_FillValue                    8�   VERTICAL_SAMPLING_SCHEME          	         	long_name         Vertical sampling scheme   conventions       Argo reference table 16    
_FillValue                    8�   CONFIG_MISSION_NUMBER                   	long_name         :Unique number denoting the missions performed by the float     conventions       !1...N, 1 : first complete mission      
_FillValue         ��        9�   PRES                
   	long_name         )Sea water pressure, equals 0 at sea-level      standard_name         sea_water_pressure     units         decibar    axis      Z      
_FillValue        G�O�   	valid_min                	valid_max         F;�    C_format      %7.1f      FORTRAN_format        F7.1   
resolution        =���       9�   PRES_QC                    	long_name         quality flag   conventions       Argo reference table 2     
_FillValue                  H  :�   PRES_ADJUSTED                   	   	long_name         )Sea water pressure, equals 0 at sea-level      standard_name         sea_water_pressure     units         decibar    
_FillValue        G�O�   	valid_min                	valid_max         F;�    C_format      %7.1f      FORTRAN_format        F7.1   
resolution        =���       ;   PRES_ADJUSTED_QC                   	long_name         quality flag   conventions       Argo reference table 2     
_FillValue                  H  <   TEMP                	   	long_name         $Sea temperature in-situ ITS-90 scale   standard_name         sea_water_temperature      units         degree_Celsius     
_FillValue        G�O�   	valid_min         �      	valid_max         B      C_format      %9.3f      FORTRAN_format        F9.3   
resolution        :�o       <d   TEMP_QC                    	long_name         quality flag   conventions       Argo reference table 2     
_FillValue                  H  =|   TEMP_ADJUSTED                   	   	long_name         $Sea temperature in-situ ITS-90 scale   standard_name         sea_water_temperature      units         degree_Celsius     
_FillValue        G�O�   	valid_min         �      	valid_max         B      C_format      %9.3f      FORTRAN_format        F9.3   
resolution        :�o       =�   TEMP_ADJUSTED_QC                   	long_name         quality flag   conventions       Argo reference table 2     
_FillValue                  H  >�   PSAL                	   	long_name         Practical salinity     standard_name         sea_water_salinity     units         psu    
_FillValue        G�O�   	valid_min         @      	valid_max         B$     C_format      %9.3f      FORTRAN_format        F9.3   
resolution        :�o       ?$   PSAL_QC                    	long_name         quality flag   conventions       Argo reference table 2     
_FillValue                  H  @<   PSAL_ADJUSTED                   	   	long_name         Practical salinity     standard_name         sea_water_salinity     units         psu    
_FillValue        G�O�   	valid_min         @      	valid_max         B$     C_format      %9.3f      FORTRAN_format        F9.3   
resolution        :�o       @�   PSAL_ADJUSTED_QC                   	long_name         quality flag   conventions       Argo reference table 2     
_FillValue                  H  A�   PRES_ADJUSTED_ERROR                    	long_name         VContains the error on the adjusted values as determined by the delayed mode QC process     C_format      %7.1f      FORTRAN_format        F7.1   
resolution        =���   units         decibar    
_FillValue        G�O�       A�   TEMP_ADJUSTED_ERROR                    	long_name         VContains the error on the adjusted values as determined by the delayed mode QC process     units         degree_Celsius     C_format      %9.3f      FORTRAN_format        F9.3   
resolution        :�o   
_FillValue        G�O�       B�   PSAL_ADJUSTED_ERROR                    	long_name         VContains the error on the adjusted values as determined by the delayed mode QC process     units         psu    C_format      %9.3f      FORTRAN_format        F9.3   
resolution        :�o   
_FillValue        G�O�       D   	PARAMETER                            	long_name         /List of parameters with calibration information    conventions       Argo reference table 3     
_FillValue                  0  E,   SCIENTIFIC_CALIB_EQUATION                   	         	long_name         'Calibration equation for this parameter    
_FillValue                    E\   SCIENTIFIC_CALIB_COEFFICIENT                	         	long_name         *Calibration coefficients for this equation     
_FillValue                    H\   SCIENTIFIC_CALIB_COMMENT                	         	long_name         .Comment applying to this parameter calibration     
_FillValue                    K\   SCIENTIFIC_CALIB_DATE                   
         	long_name         Date of calibration    conventions       YYYYMMDDHHMISS     
_FillValue                  ,  N\   HISTORY_INSTITUTION                       	long_name         "Institution which performed action     conventions       Argo reference table 4     
_FillValue                    N�   HISTORY_STEP                      	long_name         Step in data processing    conventions       Argo reference table 12    
_FillValue                    N�   HISTORY_SOFTWARE                      	long_name         'Name of software which performed action    conventions       Institution dependent      
_FillValue                    N�   HISTORY_SOFTWARE_RELEASE                      	long_name         2Version/release of software which performed action     conventions       Institution dependent      
_FillValue                    N�   HISTORY_REFERENCE                         	long_name         Reference of database      conventions       Institution dependent      
_FillValue                  @  N�   HISTORY_DATE             
         	long_name         #Date the history record was created    conventions       YYYYMMDDHHMISS     
_FillValue                    N�   HISTORY_ACTION                        	long_name         Action performed on data   conventions       Argo reference table 7     
_FillValue                    N�   HISTORY_PARAMETER                         	long_name         (Station parameter action is performed on   conventions       Argo reference table 3     
_FillValue                    N�   HISTORY_START_PRES                     	long_name          Start pressure action applied on   
_FillValue        G�O�   units         decibar         N�   HISTORY_STOP_PRES                      	long_name         Stop pressure action applied on    
_FillValue        G�O�   units         decibar         O    HISTORY_PREVIOUS_VALUE                     	long_name         +Parameter/Flag previous value before action    
_FillValue        G�O�        O   HISTORY_QCTEST                        	long_name         <Documentation of tests performed, tests failed (in hex form)   conventions       EWrite tests performed when ACTION=QCP$; tests failed when ACTION=QCF$      
_FillValue                    OArgo profile    3.1  1.219500101000000  20080730035856  20160711043434  1901119 Argo Australia                                                  Susan Wijffels                                                  PRES            TEMP            PSAL               A   CS  1901119/1                       2C  D   APEX                            3551                            42706                           846 @���t�1   @��C�- �9j~��#@N�1&�x�1   ARGOS   A   A   A   Primary sampling: discrete []                                                                                                                                                                                                                                      @���A��A���A�  B��BDffBl  B�ffB���B���B�  B�33B�ffC�CffC� CL�C)33C3��C=�CGffCQffC[  Ce�3CoffCy33C��fC���C���C��fC�� C���C���C��fC��3C�� C�&fC���C��C�fC�  C���D3D	S3D��D� D  D"S3D.ٚD;Y�DG��DT@ D`ٚDmY�Dy�fD�#3D�\�D��fD��3D�  D�c3D���D�� D�,�D�s3D�� D�\�D��D�VfD�� 1111111111111111111111111111111111111111111111111111111111111111111111  @�fgA33A���A�33B34BD  Bk��B�33B���B���B���B�  B�33C  CL�CffC33C)�C3� C=  CGL�CQL�CZ�fCe��CoL�Cy�C���C�� C���C���C��3C�� C���C���C��fC�s3C��C�� C�  C���C��3C�� D�D	L�D�4DٚD�D"L�D.�4D;S4DG�gDT9�D`�4DmS4Dy� D�  D�Y�D��3D�� D��D�` D��gD���D�)�D�p D���D�Y�D��gD�S3D���1111111111111111111111111111111111111111111111111111111111111111111111  A�/A�/A�33A�5?A�9XA�?}A�;dA�=qA�/A�"�A�I�A�$�A�"�A�bNA�1A��A���A�1A�G�A���A���Az��As?}Aq�Ai�FAg"�Ae�wAe?}Aat�A_&�A]�hAY`BAW7LAT��AQ&�AN�HAKAIVAE�hAAA=�
A;|�A8{A4{A.�uA+��A'�mA#/A�
AA�A��@�%@���@��D@��@�V@��/@��y@��@{��@o+@b�@Y�^@L��@DZ@9hs@,�@"M�@�@��1111111111111111111111111111111111111111111111111111111111111111111111  A�/A�/A�33A�5?A�9XA�?}A�;dA�=qA�/A�"�A�I�A�$�A�"�A�bNA�1A��A���A�1A�G�A���A���Az��As?}Aq�Ai�FAg"�Ae�wAe?}Aat�A_&�A]�hAY`BAW7LAT��AQ&�AN�HAKAIVAE�hAAA=�
A;|�A8{A4{A.�uA+��A'�mA#/A�
AA�A��@�%@���@��D@��@�V@��/@��y@��@{��@o+@b�@Y�^@L��@DZ@9hs@,�@"M�@�@��1111111111111111111111111111111111111111111111111111111111111111111111  BiyBiyBiyBjBiyBk�Bl�Bl�Bo�Bo�Bv�Bp�Bl�Bq�B�1B}�Br�BgmBaHBVBA�B�B�B�TB�B��B�hB�=Bn�B]/BP�B49B-B�B��B�BɺB�FB��Bq�BL�B6FB{B�B�XB��Bx�BK�B
��B
�{B
YB
�B	�B	��B	�qB	�jB	ÖB	�B	�B
B
�B
5?B
K�B
[#B
u�B
�VB
�B
B
��B
�#1111111111111111111111111111111111111111111111111111111111111111111111  Bi�Bi�Bi�Bj�Bi�Bk�Bl�Bl�Bo�BpBy?Bs5BnuBs�B��B�Bt�Bg�Bb/BW\BC�B�B�UB�;B��B�B��B�6BoCB]�BRB4�B-�B�B��B��B��B��B��Br"BMB6�B�B�1B��B�2BydBLVB
��B
�
B
Y�B
UB	�5B	�XB	��B	��B	��B	�NB	��B
CB
�B
5oB
LB
[RB
u�B
�}B
�"B
¥B
��B
�01111111111111111111111111111111111111111111111111111111111111111111111  @��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��@��;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o;o<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
<#�
PRES            TEMP            PSAL            PRES_ADJUSTED = PRES - [PRES_SurfaceOffsetTruncatedPlus5dbar_dbar - 5]                                                                                                                                                                                          no change                                                                                                                                                                                                                                                       PSAL_ADJUSTED = sal(CNDC,TEMP,PRES_ADJUSTED); PSAL_ADJ corrects conductivity cell thermal mass (CTM), Johnson et al, 2007, JAOT                                                                                                                                 PRES_SurfaceOffsetTruncatedPlus5dbar_dbar in TECH file for N-1 profile                                                                                                                                                                                          no change                                                                                                                                                                                                                                                       same as for PRES_ADJUSTED; CTL: alpha=0.0267, tau=18.60;                                                                                                                                                                                                        Pressures adjusted using PRES_SurfaceOffsetTruncatedPlus5dbar_dbar; Pressure drift corrected; Manufacturers sensor accuracy                                                                                                                                     No significant temperature drift detected; SBE sensor accuracy                                                                                                                                                                                                  No significant salinity drift detected; Minimum error of 0.01 applies                                                                                                                                                                                           201607110434342016071104343420160711043434  CS  ARFMCSQCV4.0                                                                20141020002700    IP                G�O�G�O�G�O�                CS  ARGQCSQCV4.0                                                                20141020002700    IP                G�O�G�O�G�O�                CS  ARCACSQCV4.0                                                                20141020002700    IP                G�O�G�O�G�O�                CS  ARUPCSQCV4.0                                                                20141020002700    IP                G�O�G�O�G�O�                CS  ARGQCSQCV4.0                                                                20141020002700  QCP$                G�O�G�O�G�O�C7B7E           CS  ARGQCSQCV4.0                                                                20141020002700  QCF$                G�O�G�O�G�O�0               CS  ARSQPADJV1.0                                                                20160711011223  CV  PRES            @�fgD���G�O�                CS  ARSQCTL v1.0                                                                20160711011233  QC  PSAL            @�fgD���G�O�                CS  ARSQSIQCV2.0WOD2001 & Argo                                                  20160711042008  IP                  @���D�� G�O�                