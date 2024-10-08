CDF       
      SEASONDE_HEADER_SIZE  p   POSITION  �      ,   netcdf_version        3.6    Metadata_Conventions      Unidata Dataset Discovery v1.0     Conventions       CF-1.4,IMOS-1.2    naming_authority      IMOS   project       "Integrated Marine Observing System     institution       &Australian Coastal Ocean Radar Network     institution_references        !http://www.imos.org.au/acorn.html      data_centre       'eMII eMarine Information Infrastructure    data_centre_email         info@emii.org.au   principal_investigator        	Mal Heron      author        Arnstein Prytz     author_email      info@emii.org.au   acknowledgement       �Data was sourced from the Integrated Marine Observing System (IMOS), an initiative of the Australian Government being conducted as part of the National Collaborative Research Infrastructure Strategy.    distribution_statement       ACORN data may be re-used, provided that related metadata explaining the data has been reviewed by the user, and the data is appropriately acknowledged. Data, products and services from IMOS are provided "as is" without any warranty as to fitness for a particular purpose.   
references        :http://www.imos.org.au;ACORN_data.pdf;http://www.codar.com     source        CODAR Ocean Sensors/SeaSonde   keywords      SSR    quality_control_set             date_created      2013-08-31T16:23:28    geospatial_vertical_min                  geospatial_vertical_max                  geospatial_vertical_positive      up     #geospatial_vertical_reference_datum       Sea surface    geospatial_vertical_units         m      ssr_Data_Type         	Sea_State      	ssr_Radar         SeaSonde   ssr_Technology        Direction_Finding      ssr_Ranging       Chirp      processing_level      CODAR Ocean Sensors    	site_code         BONC   time_coverage_start       2010-12-01T05:00:00Z   title         2Bonnie Coast (SA), Sea State, 2010-12-01 05:00:00Z     id        1IMOS/ACORN/au/BONC/2010-12-01T05:00:00Z.sea_state      history       �2013-08-31T16:23:28 Convert TOTL_bonc_2010_12_01_0500.tuv to netcdf format using CODAR_Convert_File.
2013-08-31T16:23:22 Write CODAR file TOTL_bonc_2010_12_01_0500.tuv.   time_coverage_duration        
PT1H19M58S     geospatial_geo_reference_datum        World Geodetic System 1984     geospatial_lon_min        @aPP�� Q   geospatial_lon_max        @a�9҉�   geospatial_lon_units      degree_east    geospatial_lat_min        �C��X�G   geospatial_lat_max        �B��+'��   geospatial_lat_units      degree_north   comment       }These data have not been quality controlled. They represent values calculated using software provided by CODAR Ocean Sensors.      abstract     lSea State data, CODAR Ocean Sensors/SeaSonde sea surface radar located at Bonnie Coast (SA), for time 2010-12-01 05:00:00Z. Sea State represents the surface sea water state obtained by merging the radial surface sea water state components from two or more radar stations. Data produced by Australian Coastal Ocean Radar Network, Integrated Marine Observing System.         seasonde_CTF_Header              /   	long_name         CODAR Sea State header     comment       oOriginal CODAR CTF header is stored in variable data. CTF header fields are also stored as variable attributes.    seasonde_Version      1.00   seasonde_File_Type        LLUV   seasonde_Data_Type        	Sea_State      seasonde_File_Version         tots   seasonde_File_Label       
CurrentMap     seasonde_LLUV_Version         1.17   seasonde_LLUV_Date        
2011-06-20     seasonde_UUID         $5CCAA4B6-5414-4ADC-8A1B-2A4BFA9E7F33   seasonde_Manufacturer         CODAR Ocean Sensors. SeaSonde      seasonde_Site_Code        bonc   seasonde_Date         2010-12-01T05:00:00Z   seasonde_Time_Zone_Id         UTC    seasonde_Time_Zone               seasonde_Time_Zone_units      min    seasonde_Time_Zone_Daylight       No     seasonde_Duration         
PT1H19M58S     seasonde_Origin_Longitude         @ao�J��   seasonde_Origin_Longitude_units       degree_east    seasonde_Origin_Latitude      �CkP��|   seasonde_Origin_Latitude_units        degree_north   seasonde_Spheroid_Name        WGS84      seasonde_Spheroid_Radius      AXT�@      seasonde_Spheroid_Radius_units        m      seasonde_Spheroid_Flattening      ?kwZ���v   seasonde_Project_Method       CGEO   seasonde_Project_Version      1.57   seasonde_Project_Date         
2009-03-10     seasonde_LLUV_Trust       [ll,xy,rb,uv,vd]   seasonde_Grid_Axis_Orientation               $seasonde_Grid_Axis_Orientation_units      degree_true    seasonde_Grid_Tool        SeaDisplay 6.6.5   seasonde_Grid_Version         4      seasonde_Grid_Date        2011-12-01T00:00:00    seasonde_Grid_Date_Modified       2013-01-29T02:02:11    seasonde_Grid_Axis              seasonde_Grid_Spacing         E��    seasonde_Grid_Spacing_units       m      seasonde_Search_Radius        F@    seasonde_Search_Radius_units      m      seasonde_Merge_Angle_Min      A�     seasonde_Merge_Angle_Min_units        
arc_degree     seasonde_Current_Speed_Max        @       seasonde_Current_Speed_Max_units      m s-1      seasonde_Processed_Date       2013-08-31T06:23:21    seasonde_Processing_Tool      =Combiner 10.5.3, CheckForCombine 11.3.5, TotalArchiver 11.2.2        p  :h   POSITION               quality_control_set             quality_control_indicator               
_FillValue               	long_name         Grid position index    units             	valid_min               ancillary_variables       POSITION_quality_control     �  F�   POSITION_quality_control            	   	long_name         $Quality flag for grid position index   quality_control_set             quality_control_conventions       &IMOS standard set using the IODE flags     
_FillValue        �      	valid_min                	valid_max         
      flag_values        	
    flag_meanings         �no_qc_performed good_data probably_good_data probably_bad_data bad_data value_changed value_below_detection value_in_excess interpolated_value missing_value uncertain_phenomenon      quality_control_indicator                 �  N�   	LONGITUDE               	   quality_control_set             quality_control_indicator               
_FillValue        G�         	long_name         	Longitude      reference_datum       World Geodetic System 1984     units         degree_east    	valid_min         �f�        	valid_max         @f�        ancillary_variables       LONGITUDE_quality_control        h  P|   LONGITUDE_quality_control               	   	long_name         Quality flag for longitude     quality_control_set             quality_control_conventions       &IMOS standard set using the IODE flags     
_FillValue        �      	valid_min                	valid_max         
      flag_values        	
    flag_meanings         �no_qc_performed good_data probably_good_data probably_bad_data bad_data value_changed value_below_detection value_in_excess interpolated_value missing_value uncertain_phenomenon      quality_control_indicator                 �  _�   LATITUDE            	   quality_control_set             quality_control_indicator               
_FillValue        G�         	long_name         Latitude   reference_datum       World Geodetic System 1984     units         degree_north   	valid_min         �V�        	valid_max         @V�        ancillary_variables       LATITUDE_quality_control     h  a�   LATITUDE_quality_control            	   	long_name         Quality flag for latitude      quality_control_set             quality_control_conventions       &IMOS standard set using the IODE flags     
_FillValue        �      	valid_min                	valid_max         
      flag_values        	
    flag_meanings         �no_qc_performed good_data probably_good_data probably_bad_data bad_data value_changed value_below_detection value_in_excess interpolated_value missing_value uncertain_phenomenon      quality_control_indicator                 �  q<   'ssr_Surface_Eastward_Sea_Water_Velocity                quality_control_set             quality_control_indicator                
_FillValue        |�     	long_name         9Eastwards component of surface sea water current velocity      units         m s-1      ancillary_variables       7ssr_Surface_Eastward_Sea_Water_Velocity_quality_control    coordinates       LATITUDE LONGITUDE       �  s,   7ssr_Surface_Eastward_Sea_Water_Velocity_quality_control             
   	long_name         JQuality flag for eastwards component of surface sea water current velocity     quality_control_set             quality_control_conventions       &IMOS standard set using the IODE flags     
_FillValue        �      	valid_min                	valid_max         
      flag_values        	
    flag_meanings         �no_qc_performed good_data probably_good_data probably_bad_data bad_data value_changed value_below_detection value_in_excess interpolated_value missing_value uncertain_phenomenon      coordinates       LATITUDE LONGITUDE     quality_control_indicator                  �  z�   6ssr_Surface_Eastward_Sea_Water_Velocity_Standard_Error                 quality_control_set             quality_control_indicator                comment       �This variable is not associated with a quality control variable. Use the quality_control_indicator attribute to determine the quality control flag for this variable.      
_FillValue        ��     	long_name         LEstimated error in eastwards component of surface sea water current velocity   units         m s-1      	valid_min                coordinates       LATITUDE LONGITUDE       �  |�   (ssr_Surface_Northward_Sea_Water_Velocity               quality_control_set             quality_control_indicator                
_FillValue        |�     	long_name         :Northwards component of surface sea water current velocity     units         m s-1      ancillary_variables       8ssr_Surface_Northward_Sea_Water_Velocity_quality_control   coordinates       LATITUDE LONGITUDE       �  ��   8ssr_Surface_Northward_Sea_Water_Velocity_quality_control            
   	long_name         KQuality flag for northwards component of surface sea water current velocity    quality_control_set             quality_control_conventions       &IMOS standard set using the IODE flags     
_FillValue        �      	valid_min                	valid_max         
      flag_values        	
    flag_meanings         �no_qc_performed good_data probably_good_data probably_bad_data bad_data value_changed value_below_detection value_in_excess interpolated_value missing_value uncertain_phenomenon      coordinates       LATITUDE LONGITUDE     quality_control_indicator                  �  �8   7ssr_Surface_Northward_Sea_Water_Velocity_Standard_Error                quality_control_set             quality_control_indicator                comment       �This variable is not associated with a quality control variable. Use the quality_control_indicator attribute to determine the quality control flag for this variable.      
_FillValue        ��     	long_name         MEstimated error in northwards component of surface sea water current velocity      units         m s-1      	valid_min                coordinates       LATITUDE LONGITUDE       �  �(   seasonde_LLUV_VFLG                 quality_control_set             quality_control_indicator                comment       �This is a CODAR diagnostics variable. This variable is not associated with a quality control variable. Use the quality_control_indicator attribute to determine the quality control flag for this variable.    coordinates       LATITUDE LONGITUDE     	long_name         Vector indicator flag      
_FillValue        �       �  ��   seasonde_LLUV_CQAL                 quality_control_set             quality_control_indicator                comment       �This is a CODAR diagnostics variable. This variable is not associated with a quality control variable. Use the quality_control_indicator attribute to determine the quality control flag for this variable.    coordinates       LATITUDE LONGITUDE     	long_name         Current vector speed covariance    
_FillValue        |�       �  ��   seasonde_LLUV_S1CN                 quality_control_set             quality_control_indicator                comment       �This is a CODAR diagnostics variable. This variable is not associated with a quality control variable. Use the quality_control_indicator attribute to determine the quality control flag for this variable.    coordinates       LATITUDE LONGITUDE     	long_name         >Number of site 1 radials which contributed to the total vector     
_FillValue        �        �  �l   seasonde_LLUV_S2CN                 quality_control_set             quality_control_indicator                comment       �This is a CODAR diagnostics variable. This variable is not associated with a quality control variable. Use the quality_control_indicator attribute to determine the quality control flag for this variable.    coordinates       LATITUDE LONGITUDE     	long_name         >Number of site 2 radials which contributed to the total vector     
_FillValue        �        �  �\   seasonde_LLUV_GRDX                 quality_control_set             quality_control_indicator                comment       �This is a CODAR diagnostics variable. This variable is not associated with a quality control variable. Use the quality_control_indicator attribute to determine the quality control flag for this variable.    coordinates       LATITUDE LONGITUDE     	long_name         OGrid X coordinate index. (0,0) is in centre of grid, increasing east and north.    
_FillValue        �        �  �L   seasonde_LLUV_GRDY                 quality_control_set             quality_control_indicator                comment       �This is a CODAR diagnostics variable. This variable is not associated with a quality control variable. Use the quality_control_indicator attribute to determine the quality control flag for this variable.    coordinates       LATITUDE LONGITUDE     	long_name         OGrid Y coordinate index. (0,0) is in centre of grid, increasing east and north.    
_FillValue        �        �  �<%CTF: 1.00\n%FileType: LLUV tots "CurrentMap"\n%LLUVSpec: 1.17  2011 06 20\n%UUID: 5CCAA4B6-5414-4ADC-8A1B-2A4BFA9E7F33\n%Manufacturer: CODAR Ocean Sensors. SeaSonde\n%Site: bonc ""\n%TimeStamp: 2010 12 01  05 00 00\n%TimeZone: "UTC" +0.000 0\n%TimeCoverage: 79.967 Minutes\n%Origin: -38.0501500  139.4717833\n%GreatCircle: "WGS84" 6378137.000  298.257223562997\n%GeodVersion: "CGEO" 1.57  2009 03 10\n%LLUVTrustData: all %% all lluv xyuv rbvd\n%GridAxisOrientation: 0.0 True\n%GridAxisOrientation: 0.0 DegNCW\n%GridCreatedBy: SeaDisplay 6.6.5\n%GridVersion: 4\n%GridTimeStamp: 4  2011 12 01  00 00 00\n%GridLastModified: 2013 01 29  02 02 11\n%GridAxisType: 6\n%GridSpacing: 6.000 km\n%AveragingRadius: 10.000 km\n%DistanceAngularLimit: 20.0\n%CurrentVelocityLimit: 200.0 cm/s\n%TableType: LLUV TOT5\n%TableColumns: 19\n%TableColumnTypes: LOND LATD VELU VELV VFLG UQAL VQAL CQAL XDST YDST RNGE BEAR VELO HEAD S1CN S2CN GRDN GRDX GRDY\n%TableRows: 493\n%TableStart:\n%%   Longitude   Latitude    U comp   V comp  VectorFlag   U StdDev    V StdDev   Covariance  X Distance  Y Distance   Range   Bearing   Velocity  Direction  Site Contributers Grid Indices\n%%     (deg)       (deg)     (cm/s)   (cm/s)  (GridCode)    Quality     Quality     Quality      (km)        (km)       (km)  (deg NCW)   (cm/s)   (deg NCW)  (#1)(#2)   (N)  (X_N)  (Y_N) \n%TableEnd:\n%%\n%TableType: MRGS src3\n%TableColumns: 15\n%TableColumnTypes: SNDX SITE OLAT OLON COVH RNGS PATK REFB NUMV MAXN MAXS MAXE MAXW PATH UUID \n%TableRows: 2\n%TableStart: 2\n%%   Site    Site         Origin       Origin      Coverage    RangeStep  Pattern  Reference   Vectors       Maximum      Maximum       Maximum       Maximum                                               Source                                                             UUID                 \n%%   Index               Latitude     Longitude    (minutes)     (km)       Kind    Bearing                   North        South         East          West                                                  Path                                                                                   \n%%                                                                                   (True)                                                                                                                                                                                                         \n%        1  "NOCR"     -37.3285500   139.8497833       79.98      2.9144   "Meas"      255.0      1550     -35.7285789  -39.0179256   141.5960131   137.3777645                   "/codar/seasonde/Data/RadialSites/site_nocr/RDLM_NOCR_2010_12_01_0500.ruv"  "D08A4CFA-BBAC-4A4D-BE4E-0820D898D559"\n%        2  "BFCV"     -37.9395167   140.4566000       49.98      2.9124   "Meas"      257.0       507     -36.9126223  -39.7995650   141.8572317   138.5988611                   "/codar/seasonde/Data/RadialSites/site_bfcv/RDLM_BFCV_2010_12_01_0500.ruv"  "21B1D2AC-A534-4E6B-851A-982888CF8CE5"\n%TableEnd: 2\n%%\n%%\n%ProcessedTimeStamp: 2013 08 31  06 23 21\n%ProcessingTool: "Combiner" 10.5.3\n%ProcessingTool: "CheckForCombine" 11.3.5\n%ProcessingTool: "TotalArchiver" 11.2.2  v  w  x  �  �  �  �  �  �  �               G  H  I  J  K  L  N  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �                          P  Q  R  [  \  ]  ^  _  `  a  b  c  d  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �    "  #  $  %  +  ,  -  .  /  0  1  2  3  4  \  ]  ^  _  a  f  g  h  i  j  p  q  r  s  t  u  v  w  x  y  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �           /  0  6  7  8  9  :  ;  <  ?  @  B  C  D  E  F  G  H  s  y  z  {  |  }  ~    �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  	   	  	  	  	  	  	  	  	  		  	
  	  	  	  	  	  	  	  	  	  	  	  	  	  	A  	B  	C  	D  	E  	F  	G  	H  	I  	J  	K  	L  	M  	N  	O  	P  	Q  	R  	S  	T  	U  	V  	W  	X  	Y  	Z  	[  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  	�  
  
  
  
  
  
  
  
  
  
  
  
  
   
!  
"  
#  
$  
%  
&  
'  
(  
Y  
Z  
[  
\  
]  
^  
_  
`  
a  
b  
c  
d  
e  
f  
g  
h  
i  
j  
k  
l  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  
�  '  (  )  *  1  2  3  4  5  6  7  8  l  m  n  o  v  w  x  y  z  {  |  }  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �  �          6  7  8  <  =  >  ?  G  H  I  |  }  �  �  �  �  �  �  �  �  �  ���@au�~��w@aw�܇U@az.�G>�@au�5��@aw�U�r_@az,u��I@a|c���@a~���M^@a���k�@a�����@au��&�@az*RN�m@a|a�&H@a~��Q��@a��c���@a���i@az(05Q�@a|^t��S@a~���9:@a����U�@a�:�R�@a�7z��@a�����@aw�75 s@az&^A�@a|[氣�@a~�����@a�ǒ0�@a�38�{@a�i	y%�@a���h�@a�ԥs�o@as����@au�O�@aw�w�e@az#��Q@a|YZy�@a~��Ѣ@a��,��@a������@a�.�}/ @a�d]w�\@a����Vs@a�� .s�@as���gC@aw�ґ1�@az!�v�@a|Vυ�@a~�̼ܕ@a��Ȳ��@a��Ûˣ@a�*�׌C@a�_�eͺ@a���F�@a�ɞD#E@a���(א@aa�]�(�@ad�,�@afF�/��@az�eͺ@a|TF=��@a~��?�@a��f�;�@a���{A�@a�&��(F@a�[߽@a������@a��!H@a���-K�@aa��x�=@adO�[@afH23X�@ah|Y�RU@aj��r[g@az��;@a|Q�ne8@a~��n��@a��-�@a��)���@a�"J�S!@a�Vjo�c@a���N�{@a����@a���m�@ad&�@afI�*Q�@ah}��!@aj�X���@al�c>�@ao��};@a|O8��@a~��L@a���t��@a��`[�j@a��l�@a�QɋϬ@a��+�hc@a����>B@aR}�5��@ah~�8�@aj�/�D�@al���@ao��};@a|L�6��@a~�oz@a��M��@a��&�@a�� �@a�M+a��@a��r�@a�����@a���i
@a�9҉�@aPP�� Q@aR�^�a[@aT�8�1>@aV���J@a[N��K�@afM;��V@ah� �ߒ@aj�R)�@al��"�j@ao��};@a|J/���@a~}D�"@a����@a���
��@a����@a�H��z+@a�{kE�8@a��D�@a��D�%@a��<:@aPVa5��@aR���+L@aT�<K�@aV���t�@aY �ؐ@a[R��k5@a]�9@afN��O�@ah�a�s@aj��:��@al�W>
@as}ǫ��@au�B�@aw�쪹@a|G����@a~z%`�@a�����=@a���@@a���!�@a�C��{@a�vg��@a����*@a��B�Ux@a���L�@aR�9H��@aT�=<�q@aV�B��"@aY$Jb#�@a[VS^K�@a]�^�@afP��:�@ah��O�@aj���tP@al�����@ao��};@aqJ��@as|�.�%@au���@aw���@az�t�@a|E-fj�@a~w:(�@a��E�b@a��P���@a�Y�֔@a�?a	/T@a�qf�Y@a��j��@a��lx�@a�l�@aY(sQ0t@a[Z���@ah��p(@aj��ʉ�@al�,_�@ao��};@aqJw���@as|py@au��E�N@a|B�e�y@a~tP�T�@a�ב���@a�	0��@a�:͑�@a�lh��@a��I�\@a�ϙ�G@a�.�(�@aV�gP@ad"�2"�@afS��q�@ah� e�@aj�[;��@al�|��@ao��};@aqJjK�@as{H�j|@au���)`@awݽ�z@az����@a|@0��@a~qh���@a���Ҙ�@a��՟�%@a�	�LH@a�6<��&@a�gm�b�@a���W�@a����f@a����D>@aT�.;|�@aV��M�V@aY0��)@a[a�E�?@a]�T*��@a_�!�:@aa���n@ad$�%j@afU��`@ah�^�"S@aj�/v�@al� �Y�@ao��};@aqI�L��@asztpe@au�E]�"@aw��<@az���Y@a|=��%@a~n��J<@a��O���@a���F6@a� ��M@a�1��@a�bu�}�@a��:��a@a���&��@a���$m�@aT�#m�R@aW��@�@aY4ߥ�e@a[e@a @a]��^d9@a_��γ@aa�i騦@ad&�B.@afW5;K0@ah��ճ�@aj��|�@al�jL��@ao��};@aqI9�U�@asy�}�@au�Fy@aw�n��F@az
�ڸH@a|;9�Q�@a~k�I+�@a����<@a��c��V@a���A@a�-#N��@a�]�y7$@a����5|@a��5ZT�@a��P@aT��km@aW		��x@aY8��^�@a[h�-�'@a]��x��@a_��;�@aa��
��@ad(���@afX�ch�@ah�؁5�@aj��
c0@al����6@ao��};@aqH��
@@asx�ܗE@au��eĀ@aw�ȃ��@az� O�@a|8����@a~h��<Y@a���nv@a�ȭ�O@a������@a�(�R��@a�X�6�@a���6�@a��pv@aW���@aY=�AR@a[l��6T@a]�8���@a_��a�A@aa�Z�1b@ad*�ID@afZ�a@ah�U�Z@aj���:@al�=E۬@ao��};@aqHf��@asw�N�W@au���@aw�#g�@az���_@a|6H��@a~eڅ4@a��k ��@a���:�!@a����$@a�$F��@a�S��Ց@a��'gM@a���=��@aYA6`�@a[p[GNs@a]��o�(@a_Ψ��X@aa����@ad,��m�@af\$��@ah�O��@aj�z��A@al�W>@ao��};@aqG���7@asw),I4@au�T]Of@aw�"��@az�G��@a|3���@a~b�B+@a��"w#M@a��H��@a��m�X@a�����@a�N�Jj�@a�}��{@a���{@a]�����@a_цo�*@ab F}@ad/�xh@af]���t@ah���/@aj�LqȚ@al���@ao��};@aqG��p@asvWu1�@au� \F@aw���w@az�3�@a|1]�}j@a~`w	L@a���%�@a���S"�@a��U^ f@a��^�@a�I�k><@a]�n�L@a_�b���@ab��C�@ad1�c�@af_j^B�@ah�â��@aj���C@al�w���@ao��};@aqG,D+�@asu�_*2@au��Dx�@aw�9���@az �a��@a|.�c��@a~]AYf�@a���xW*@a���xk@a��?�zN@a��q��@afa��i@ah���Ua@aj��2x"@al����@ao��};@aqF����@ast���S@au��)�@awИ3h@ay���T@a|,x.@a~Zf�C%@a��T��@a��A�@a��,/2�@a[���@a]��c@a_��[�@ab�A�@ao��};@aqF[�3�@ass�u:?@au�n��@aw�����@ay���@a|*��@a~W�&��@a��З]@a���8p�@a[����a@a]����v@a_��Հ�@ab
��@aqE� }@ass�Q�@au�7B�m@aw�XB�5@ay�x��M@a|'�_ݶ@a~T�y�@a����U�@a[�W2�@a]�1f�@a_��=&�@abyUVt@aqE�0�K@asrFnyZ@au� @��@aw˹�V@ay�rm�@a|%*��@a~Q�Ӥ@a�~����@aR����@a]�GOI�@a_��M�@ab��p�@au��bh@aw�d{@ay�mzV�@a|"���@a~O��@aP�1�#�@aR� �t@aU	�u@a]���� @a_�h9�=@abP��@ad=:R�%@au���<�@aw�`2p@ay�i�P@a| S&�@aP���$�@aR�J��@aU�G@a]��3"@a_�8�}�@ab�\��@ad?<�T@au�_�'@aw��o�@ay�f��"@aR�(��@aU��k@a_����@ab"��-@aso
��@au�+���@aw�H�l�@ay�eXIm@asn@��@au���/@awî�){@au�ń/����C���L{��C��X�G�C��\[J��C|���C{�[���C{�b|���C{�����C{�s���C{�|�y#�C{�3���Cu���Cuc�ю�CuG�b�Ct�y=��Ct�t���Ct�?���Cn"`}Z�CnܻW�CnzVt�Cn�����Cm�G��s�Cm�cU�Cmӌ�nv�Cg=N?(4�Cg7Y2�=�Cg0���Cg'x��Cg�+A��Cg�}d��Cf����Cf�6,�Cf��m2�C`Z/ ~��C`V�$��C`RAt�C`LN�+��C`E	���C`<q�VL�C`2�;��C`'JǤo�C`�C��C`۰�_�C_��6�O�C_�"����CYo���CYg/���CYa>�8��CYY��؅�CYQf$!G�CYG�R�CY<Fl�CY/��n�CY!�w<�CY�/-�CY.�i4�CX�\�CRn�¦��CRv*���CR|,���CRv*���CRn�¦��CRfWL���CR\rǝ��CRQ=	u��CRD�v$�CR6��1�CR'��p��CR6}j��CRh����CK��5v��CK��N�CK� m�	�CK�����CK����X�CK��N�CK��5v��CK{DC���CKqbB�7�CKf/����CKY�C�I�CKK�n�>�CK<�a6|�CK,:��CKq�M��CD�����CD��}8:�CD�}�k��CD��N��CD��#K_�CD�i��;�CD����_�CD�,2���CD�M�z��CD{�O��CDn�CL��CD`͠1c�CDA9�3��CD/vP��C=V4��-�C=�Z���C=£~��C=ě��T�C=�DBO0�C=�����C=�� ��C=�4�L{�C=����C=����o�C=u�����C=f��HC�C=V4��-�C=DvQ���C=1hW�.�C6Yrb,�C6k+���C6{����C6��m���C6��81��C6Ϛ���C6�2���C6�z����C6�r�|��C6��)=�C6�x��C�C6��Q6S�C6��`A�C6��81��C6�v����C6��m���C6{����C6k+���C6Yrb,�C6Fip���C/nj@�z�C/��P��C/������C/��	�a�C/�[�=`�C/��G���C/��>��C/�o��[�C/��6��C/�M��F�C/�E�X��C/�M��F�C/��6��C/�o��[�C/�Ra̤�C/�́Mr�C/��>��C/��G���C/�[�=`�C/��	�a�C/������C/��P��C/nj@�z�C/[g.�B�C(�l�C(�l5�@�C(�|s���C(�=&���C(ήN\��C(���N�C(�@���C(��ZI�C)6q��C)����C)�vc4�C)����C)6q��C(��ZI�C(�@���C(�[���C(�'���C(㣨��C(���N�C(ήN\��C(�=&���C(�|s���C(�l5�@�C(�l�C(�]����C(p_�l&�C!�-���C!��4��C"���\�C"��і�C"�C��C"�2��C"�C��C"��і�C"���\�C" �M��C!�wu�c�C!��4��C!�-���C!�\����C!�Q���C!�����C!�Mi?_�C!�Th7!�C�9ܚ��C�L��C"�ĝS�C'i�T��C*�)s��C,���B�C-K����C,���B�C*�)s��C'i�T��C"�ĝS�C�L��C�d"��CF9�5�Cy1DF�C�]tO]�C���{�C�9ܚ��C�2ؚ`�C��IA��C�7�`�C�D�D4�C���C���l�C Ǧ_�C-��Y�CG���C"����C*�rC��C1�c��C7�w�+�C<,����C?pXW��CAe��\�CB���CAe��\�C?pXW��C<,����C7�w�+�C1�c��C*�rC��C"����CG���C-��Y�C Ǧ_�C���l�C���CӾX���C����C�1�R��C����K�C�~N��C��Z�C!��� �C-�B�C6�a��C?R%f��CF}����CL[�%�CP쁝��CT/,=v�CV#���CV���?�CV#���CT/,=v�CP쁝��CL[�%�CF}����C?R%f��C6�a��C-�B�C!��� �C��Z�C�~N��C����K�C�_lw�C�5?�C���6�C��%/�C����C*c����C6��k��CAՍe��CK�2E��CT��C[;���CaH�"�Ce�#���Ch�����Cj���@�Ck�ܘ��Cj���@�Ch�����Ce�#���CaH�"�C[;���CT��CK�2E��CAՍe��C6��k��C*c����C����C��%/�C�uD��C�߷��B�1�Y4�B�?+���B�K����B�V��3�B�`Y+��B�h��$�B�o�[aP�B�u�f�A�B�z^j�b�B�}��P�B���V��B��8����B���V��B�}��P�B�z^j�b�B�u�f�A�B�o�[aP�B�h��$�B�`Y+��B�V��3�B�K����B�?+���B�1�Y4�B�"���*�B�I����B� �cc}�B�S�k]F�B�`H?3��B�kT���B�uѓ��B�}�fܮ�B������B���R�x�B����o�B��P��,�B��C�C�B���p7�B��C�C�B��P��,�B����o�B���R�x�B������B�}�fܮ�B�uѓ��B�kT���B�`H?3��B�S�k]F�B�FJg,_�B�7X[��B�' <��B���}��B�)���B��A���B�9S��B�\\�)�B�4M��B񣿍I)�B��*��B��N��B�f�2�B��N��B��*��B񣿍I)�B�4M��B�\\�)�B�9S��B��A���B�)���B�u�e�B�h���B�[l��B�L j��B���ĺ�B�z��J�B��6���B�	�&��B�ߕ�-�B�ihyf�B껧
�d�B꽙S"��B�?kO��B꽙S"��B껧
�d�B�ihyf�B�ߕ�-�B�	�&��B��6���B�z��J�B���ĺ�Bꉻ���B�}j���B�o�uh�B�Ȇ���B���P�B��L���B��>%�}�B���gC�B��>%�}�B��L���B���P�B�Ȇ���B�³nV��B㻓�e�B�'���B�q}��B�n�p&�B� �T	�Bܳ��u�Bܾ�`��B��ѻI�B��:?���B��7��B�����T�B���U��B��`_��B��*"A�B��XA	��B��:?���B��ѻI�Bܾ�`��Bܳ��u�B���W�F�B���4R�B��v����B���dʅ�B��z_A��B������B��O}��B������B�������B���dʅ�B��v����B���4R�B��p����B��i0EB�B���C�B��{����B�����B�"�r�B�
�Nq�B�d�J�B� �Q5}�B��{����B���C�B��i0EB�BǸW��1�B���z��B��t�3�B�C8d�B�~J���B��.	(�B�-����B�C8d�B��t�3�B������B���o��B�� 'G�B������B�M���B�"��r��B�)��i��B�4��B�/��E�B�)��i��B�"��r��B��Sj
`�B��`_��B��Ū���B�%;"��B�.����B�7>Z���B�>Qtf��B�H�Q��B�D��+�B�>Qtf��B��W����B�g���B�CrE���B�K̇,��B�`\a)��B�]%u��B�X���P�B�R��e��B�tߥ�e�B�q�gG7�B�m,SE!�B��+'������]����̎����]��������D�X:���Ѿ�5Ӿ�5Ӿ�
���D�������Z5ӽ�r���<���ۿ(�F�G:�����cs�Ǚ��TL�	&�-�v����������ݾ�����L�U�C�������	���뾾�ξ��Ⱦ��\������Dh�+�c�'?���rž�y=���7��ܱ��[-���^����㽾��T�
��>�H,<���:O�������{���־����4��c4��ԕ��#>�u>zީ�c�۽\�ʽ�r�v5��F�&����N����t��]ᾋYݾ�h��������jT�ʦM�I*1����� �b�ρ�1���ξ�0���&�� ��*���Mj���ܾ��Z� M��|eA��V������/Z�-��Jw�����Ԧ#�ܵ4�ƀ����L�	�J��-�$�-��|F�R��8	��1�A��Aiþa�l7a��+���B�-��N��׮��&������݊۾�`A�d0�2M�uy�C��}K�+�
@��(�N��9	l�:�e�B�w�YM��V�E�q�����Ёþ��Ȓ%��X���7������U\��ݿR�ﳿ ��N۶��=q�ߏ��F_�΅�9	l�9�`c��uy)�e�H�]�I�d��k������Q�(Ɠ��˧��x�������Fܾ�k������Ĝ�;ͿH���"?�D!�¤�#� �?��Y#��{�s�v���B˨�.1Q�0���c�����]���ᾞ����\��e��۾���%�n�?��0-��u;��]�?�Y	l�V�$�Cn�)�۾I'��C��S��҃��G0�)�۾h.��������W�濈��~|��f��A�S�a�MU��{ȼ]Y�R�Ƚ�<�p�4Y��s���<�`��"!C�) ?��2M��޾E8�^��Gi��2W ���Y�X�(��tҾ��A�Ĺ̾�� �ܽ����D���@u���rq�W�����l��pO�曾2k���q7��������ܽ�&-��ޓ��*o�6��J5��C")�Jb$�()J�gH�m�E�������������*ؾӿr�����1c4�'�������������V��/��,f�����A���pz��J8�ϰ���j��pe� �ھ �/{��WQ�x澆����얿$�־�`���Ⱦ����5j���8�������W�ʶ�����ی�{����ƒ��Ƨ�ٞؽ��I��Խ��,�̝���
�s�������<��WS��}��	���s���=��������}��RT�����������2������轔1{�TL���v��GE���e��W?�֌i�ؾ<л���t���ξ��w��믾⡶������ľ�u%����1�Y!��e���S�������T�@Y!���ϽT��~�t��T��:�(���wɛ���T�´��3���Ԋ���g̾�&Խ)?)�J�t�a�񽫾ʽ�Ĝ���a�������--�;���������2 }�s����˾���������[���[��˒���Ž�'=�m	���1��?Ѿ(����%�+�@�O�ӾD�־e�׾{��"&��\�Ͼ�d��
���\��$����?��h
��^����;y򻾆|��k���c�O��)s>��&=?�ʶ��Ϫ��Q��E��=��� ���͊��i쾌M���&l>��?/o��d1��|1��w��e�������������������־ >�?���o�����ས�;�^_��������ݘ>_)
;F����k�Y������A6��%o��O7��,=�����RT��k��2��}l��NϾ	Q���3����{�D���ƽ��ʽ�����������n�Aݾ-q�
���׼`u��UW�/<��X%�;2�                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             ���|�  =B&�|�  |�  =B�8|�  |�  >�c>ԕ>ԕ>�r|�  |�  >��t>�xl>ԕ>q�j>�a|>��>9�><��>E�>r�W>��=��H>�=�Q�=�}�>E�=���=�/�=�A�>��><j>)^�=���=�
�=#S|�  >Ov`>�=͞�=��>u%>���>/�W=\=lV�=u|�  >G�>s�=�N�=�$t=�֡>8�>1&�>�r>q=�x=Yc=5s�=V8�>LM> �=���|�  |�  ?	�>)�> 'S>)_=g�f={~�=d��=g�f=D��=s�E=���=��R==�|�  |�  |�  >�=��.=|PH=Gy�=��R|�  =lV�=��/=��]=��.=jJ�=@�|�  =���=)�=�A =��=n��|�  =�a=�9X=�$t=���=Z��=��=O��=��/=��v>R�=E�8<�~�=*͟=-B�=0��>[�>L�=�%F=�!|�  =�#:=���=��
=�Ov=t��=��L=���=��S=d%�=~\�=?�[=IQ=-�=)*1<҈�=$��=%�|�  =��8=�2�>H�=Τ�=��=�|�|�  =d%�==�\)={�m=��=�*1=�u%=���=�M=AT�=0 �=�=F��=$��=-B�|�  |�  =��=� �>m]=��r=��=�,�=�A�|�  |�  |�  |�  =�A�=.}W=}!�=�d�=��
=�D�=.�2=f��=[�="�x=ix�=[��=�=�=R��=B&�=�<�=�L�=N�=B�8=?�[=��=�R�=�?�=_;d=�q=��M=O��=w�=
q�=�v=>v�=
q�<ڹ�<���=~(=��=��={�m=v�F=Ws=U�=$��=L��=x��=y	l>�8=�-= �.<�u|�  =7�4=M��=$t="3�=F��=
	=��<�)_<��<��<�Ϫ<�IQ<�}W<�C=��<�~�|�  =6�}=== 'S=!��=8��=H�:=�*1=_=+<�0�=��=�=N`=C�=.�2=R�=%=~(<��<��`<��|<���<�<�i<�d�<�L/<҈�<�-�=��<���<��m<�	l=��=\)=��=49X=>v�<t!<�e�<�D�=0��<���<�?<���=E�8='��=0�<�e<䎊<���<���<�,<<�Mj<�D�<�#�<�&�=��=���=�N=_<�<6=�-=�v<��w<�o<���=(�T<�A�<���<���=��=>�=;��<�~�<�<��w<�w�<Ʌ�=%<��Z<�+<�+<���<��<�)_=��<|PH=�v<�0�<�_|�  =w�<���<��T<��=4�3=poi=N`=>ߤ=!�<��3<�<�A�<���<h�<�o<be<�9X<V�a<Np;<jJ�<���=+|�  |�  <�Q�<ۋ�<�g�=�P=�P=;/�=M=u<�m]<�m]<��N<��<u<y	l<��p<�3�<2��<���<��f|�  |�  <�j=��<�1�=,��=:*=5��=1[W=��<��<�J�=�<ě�<�-�<��<��<ۋ�<��<��3=��=��.=���|�  |�  <���<��Z=.{=B&�=6E�==�<�L/<��=��q<�1|�  <���<�zx<���=K)_<���<���<�i=x��=��'=�Dh>K�:>h�T>	�^<֡a=%<�W�<�~�<���<�&�<�D�=.{=��q> =�\�?%�|�  <�A�<�s=3g�|�  |�  <�1�=	7L=6E�=R�=˒:>4m�=&�<��=\)=6�}=�M<֡a=�=9�Z>o=#�
=�v=7�<��<�D�<��m=J��=2-=%==��
=ݘ=ݘ=7�|�  <��<���<��=A��=#�
=$?�=.}W=Gy�=!a�=�=�N<��<�L/<�m]<��<?�[<<j<SZ���]x�eu;�,2#��]x�c�I�,2#�,2#����K
��K
��f��,2#�S��ߏH��!��K
�G8�9�8��|ؽ�2��&����:�1�����#�V�����Qֽdd���H�� ���o?�����$�M�)Ⱦ+Խ�Ƚ�&����o��
���b8�å<�s#x�-ڹ�����������k��q����wq����c���xԽ���V<1pO>)���)��� sX����z�e��򑽑�V�ܗ��wq�]!�#S>1��>$Jc=!�ֽ@Y!<��:���>Wpz>������x�(�CA��\	��a�s;U��;[���[ؼ(�d�sw[>7Q>��^>��>���>����)J�t�ؼ�Y�B=���=8��<��<�������9�"��>MW�>���>���>�2v<��	=�%=��=�p�=O�Q<�3��\]d�ě���h��$�Yjj��=��>�M��jT>rG>�>V�)>`4n>�2v=���=�9.=�3�=��[=��*<�t�;2B;ECl��>m�wF�EF
���<z/�z�e��k���/��A =��=�K=��>(��<1pO�Ѣ�
��=�ff=���=��=6��=�M�=W>�=�a<ݗ��vjT��%����Ӽ�����l�7�����/� sX=�J>4Fs>A�s=®�=�_o;����Zf���J<�� <���=���=��O=�݃=�82=r2M=�pz=���=��=t
)=!�Z�|����e�>8��>R�n>���>.Pƽb�:�";�IQ;�s.=V��=���=��>��> �=�*=�==ͩ <�Ǹ=���=�2�>�l>Y��>5f�=�O7=LN��	LD�[7ʼ;��;�?>�xW�$!���<��-=�_>�L>%3�=�n�=��;>=��s=��2��_�xOM�?�@����� �=돛=V8�=���=�?=�D�=�R�I�W�	V��<9P���7����(mr�<��3>[l>>%KI>�>E�=�.�=���=`Խ�.�Б�#�P��/<��=<�=;º<�D�=�c=p��=�5�����c_�f�ͼ/%<�d�=	�
�H�:=+=5��>x>3��>.ƽ>[W=�ô=ʦM=(�F=�$!��tҾH������mH:ě��c��E�ô�<�=���>d�>M\���Hj;�]x��6e<� �=R�J=�=�Bp=���=��>?��>='=>j�=�tS�^ ҽ٤��X;�C������'ŭ�\z�X�<�4n=]�=���=��>�<�J�~��;0�|=+=*E=�Y=�^t>;�=�/>^ �>3��=.)s=O,���m	��<K��<A~����{=�����?��P��?�=F��>�=�a(=Nܼ�҉�rϖ�t!<E�N=���=�y�>?>>A%�>Ez>G�=N�3<�O߾W*�X���g��<B�F�����T��*dü4f<��<�K�=�ԼOk伜#�=FT=�'�=�I>A��>�=��/>8~|=d��*+�W�	���Ͻ����y��т��	/o��f������?<E=zxl=�7�>6r2>w�
>��F>h@�>q=z/�"r�����Xd�K�$�	9��0�<�r�=�H=��D>VC>��Y>��3>� >��=���������t���=�Ǔݽ佺=��=�#x=���=�Z2>.>S@N>�T>�%�>��]>5in�ʫ��ԟ��=曾0H=�)�=ң=��=�{>.N&>^7�>�?S>��m��Ͻȹw�����=��> �=�i�>T�>�->Vݭ>���?�n�yX�O�$��n�w>	�W>2�=��3>2�>�|���!��ȟ��A������c�ྃ+V��T=��=�,�=ǎ�=�l8��]N��5Ӿ����E����v6�{�L�u�����<łV=ƿ`���W�d����������<���=Q.Ƽ��L=��`>2ܱ=�/n>q/                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             ���|�  <��|�  |�  <��T|�  |�  =��=ܑ�=ܑ�=N`|�  |�  =�+�=ߤ@=ܑ�>�>�=y	l=w��=��t=�,=-��=�bN=Em]=�\)<�~�<�i==<��.<���<��&=�o<��
<�$=�-=�-<�M|�  =+<��F<�L/<���<��=!��<��E<��E<��<�w�|�  <�!�<ڹ�<�O<`u�<���=u>..�=���=���<�G�<�Ϫ<�<6<�Ϫ=��=%<��|�  |�  >IQ�>_=���=�!-=sMj=��s<�p;<ě�<�a�<�m]<ě�<��<�$|�  |�  |�  =��=���=���=���=�u�|�  <�M<���<ȴ:<ۋ�<���<�+|�  ;��=S�a=��-=��q=��/|�  <҈�<�҉<��<��<��Z<͞�<49X<K)_;�D�<�a�=���=T��=���=��=��+>	7L=�>�=��7=�8�|�  ='�<�e�<��=O�<ě�<ě�<��'<h�<49X<�6z=��=���=�a=��F=��q=W��=^҉|�  =��/=�n/=��c=x7�=M=I��|�  =>v�<�j<�1�<ѷ<ȴ:<��w<g�<�o<ȴ:=��=���=��X=ě�=W��=�~(|�  |�  =�]d>Z��>\w�=kC=zC�=$?�=P|�|�  |�  |�  |�  <��m<��<��?<ڹ�<��<���<�+=��=��#=��=ԕ=�"h>bN<��`=V�a=�q=v+l=:^6<���<�i<�D�<��<� �<�w�<�q�=�g8=���=�ݘ=��	=�s�=�1=�y�=g�<�C<�Mj<��E<�7�=b�=\�?=`u�= 'S<�!�<�<Ʌ�<�IQ<���<�_=�e=Õ�=��T|�  =��=��=E�8=�bN=�[�=�[�=��n=gl�=X��=SZ�<�x�<��?=�=2��=_;d=E�8|�  =7�=
	<�e�<�9X<��<Y�?<�IQ>�*=ѷ=��=�
�=^i�=a��=��=0�|=���=s�E=cS�==<6=>�=K)_<��=W��=@7=M��=\)=-��='�=0 �<�<�A�<��<���<XD�<� �=ⶮ>4=�U2=��/=���=�$=ح�<� �=�bN=�C�=nc =A��=y�#=�8<�҉=�YK=T��=M5�=�v=!a�=3�|=�=�=��=�o<���<��=ح�=�֡=�#�=��8=�%F=Τ�<��=/��=SZ�=Z��=F��=X��=��>�:<��[=��=/O= 'S=F��=<�=M=��=$t=W��<���<���=�=��s|�  >�p=���=�1�=��=Uf�=W
==@��=��=��|=���=W
=<��,<��Z=T,<=b�==�="�x=�&=T,<=���=v+l=Fs|�  |�  >&>TFs=[�=J��=e�=Gy�=T��=x7�=��=v�F<�C�<��=?H�=E�8=5��='�<�	l=d%�=���|�  |�  =���=ڹ�=�\)=<j=.�2=��=6E�=QN<=�ѷ=\�?=0�<��$<�=�=O�<�,<=	�'=K�=�!=�-w=��|�  |�  =$��= 'S=P�`=O��=��=O�<�W�<�\)<ě�=��|�  =p�=y�#=��&=-��=�&=#n/=u=7X=�=!�=I��={�m=(Xz=�d�=���=��;=���<�=hs<���=��<�u�<�Z�=5s�>(Xz|�  =���=�!-=�@O|�  |�  <�{�<Ʌ�<�m]<�ߤ=��=�  >(Xz=��j=�c�=�J�<���<|PH<�@�<��N=�&>L��>*��>)�=}�=���=��m>#S=��<�<�q�<�#�>Q4>Q��>m�|�  >F�> ��>E9=R��=e�<�6z>�	>���>Ɇ>K^=�-=<�<�Mj<�?=��
= �
<� �=��                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         �|�  @�ff|�  |�  @��|�  |�  C3�qC��C��BG��|�  |�  C�j=C�"�C��C���C�.B��RB�ffCE�aG�B���B�B�B"�
B���Ap��A�=q�;�A&�RA-p�A�HB�L�B 33Alz�A�33A�Q�@���|�  ��\?s33@���A\)A33B��A�G�AYAw\)@�\)|�  �z���G�����@��R�L������Cy��Bʞ�B�{A?\)A<  @���A3\)��A���ff|�  |�  Ă��CO5�C#=qB�=qAݙ�B�RA&{A�H@�ff@�G�A!A���@c�
|�  |�  |�  C
=B(�B{A�p�B�ff|�  @`��@1�?�Q�A
=>�G�@��\|�  ?��A���B���B7��B1��|�  @ƸR@θRA��AS
=@��
���H@l��@�=q?�
=��{B�AEBBBD�AÙ�Cy��C8��B��B��|�  A/�
@У�@��A�
=@�
=A.�\@�ffA��?�p���
=A�\)B��A��B:G�Ab�\A|��A�|�  B[Q�B^�C#^�B
=Ai�A���|�  A�ff@$z�A�
@���A=p�A<z�@�(�@��� Q�BS33B.33A�=qB��A|��A��|�  |�  B�\CH�{C\O\A�p�B��A�G�A�(�|�  |�  |�  |�  �33@��
AQG�A@z�@y���h���G
=BT�B_Q�A�Q�B4�BEp�B�G�@�p�A�  AG�A�
=AeAz�A.=qA&{AK\)A���S�
�\)A���B0\)A�G�A�G�A�=qA���BG�AG
=@u�@x��@�@��RA��
AK
=A/�A�Q�A�A&{A	��@�ff�#�
�nffA�Q�A��A$��|�  A�z�A��RAO�
A���A���A�ffAX(�AffA%�A#�@j�H@6ff@��@���A\(�A/�|�  A���A+�A�@�Q�@�=q�#�
�,��B�A���@��BC�Ap��A�ffAffAn�RA�ffA<  A�@��
@�(�@ə�?˅A
=q@�z�@�33@��A=q@��RA
�R@�G�@��@��@aG������'33B*ffBdff?�p�AA�AnffA�A;�@��A�A�Q�AJ=qAAz�A��R?���A   @���@��
@�(�@�G�@!G��qG���\)A�A ��?�\)?޸RBG�A'�@G�AMp�A��R@�{@b�\@��A4��AyG�AIG�@��HAj�\@�33?�G�?�Q�@�H@0��@K�?����(�?xQ�@\A��?޸R@?\)A   @�ff|�  A���@��
@�@Dz�Ac�A��As�Ao�@�G����H�	��?+�?h��@+�=���ff�$z���J�H��=q�dz��E|�  |�  �&{��@C33AffA�Aj�HA��A�
�   ����=�\)<��W
=�Q��n�R��33��\)��R����|�  |�  �z�H�5�?0��AY��A��AO�
ADz�A�?˅�У׿�
=��(�������\��z���{���
�(�B;��B7��B8z�|�  |�  @�����\)�&ff��G��C33���
�n{�
=��  ���
|�  ��=q�����Ak
=@W
=?�  ��H�  >�\)��  ®�R�ff�7��[\)�X  ��\)��
@�ff@��>�G��p  =�G���ff�J���k� |�  ��  �N�RA��|�  |�  @��z��1G���\)��\��\B9�׿.{A��A��R@���?�\)���\���
�=qA�G�B-�
B3=q�1�@�ffAD��B�HA*�R@�?��H�,(�A�
=A�ff?��|�  AB�RA-ALQ�A��RA$��@�33�\)�D
=AL  A�\)A�Q�A@�33@W
=Ap�?�33?333�0��	
	

	

							



	
	
	
		
	



				
	
		
			
	
		
		
	


		
		 	
#$
*'+)56G1DLO-DO9���		
"!	#%	

	!	


		
		
	���			

	
	
���	
�����	
����� 	
���� 	
��������� 	
�����������	
���������� 	
����� 	
������ 	
������������ 	
������������ 	
������������ 	
����������� 	
���������� 	
�������� 	
�������� 	
���� 	
���� 	������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������                           									










���