/* NOTE - This JavaScipt code is copyright (c) Alan Morton and is to be used solely
          within the Transverse Mercator Calculator HTML document. You must not use this JavaScript in any other way
          without the prior consent of Alan Morton */

function ClearGridRef(Form)
  {
  Form.Easting.value=""; Form.Northing.value=""; Form.GridRef.value="";
  }

function ChangeNS(Form,South)
  {
  if (South) Form.NS.value="N"; else Form.NS.value="S";
  South= !South;
  return South;
  }

function ChangeEW(Form,West)
  {
  if (West) Form.EW.value="E"; else Form.EW.value="W";
  West= !West;
  return West;
  }

function ChangeMeridianEW(Form,MeridianWest)
  {
  if (MeridianWest) Form.MeridianEW.value="E"; else Form.MeridianEW.value="W";
  MeridianWest= !MeridianWest;
  return MeridianWest;
  }

function convert(Form)
  {
  with (Math)
  {
  TM2LL=false; OK=true;
  Deg2Rad=PI/180.0;
  with (Form.SelectArea) Area=options[selectedIndex].value;
   Alpha100km='VQLFAVQLFAWRMGBWRMGBXSNHCXSNHCYTOJDYTOJDZUPKEZUPKEVQLFAVQLFAWRMGBWRMGBXSNHCXSNHCYTOJDYTOJDZUPKEZUPKE';
  if (Area=='UK')
    { // British Isles (Airy Ellipsoid)
    F0=0.9996012717; // Local scale factor on Central Meridian
    A1=6377563.396*F0; // Major Semi-axis, Airy Ellipsoid
    B1=6356256.910*F0; // Minor Semi-axis, Airy Ellipsoid
    K0=49*Deg2Rad; // Lat of True Origin
    Merid=-2;
    Form.Meridian.value='';
    L0=Merid*Deg2Rad; // Long of True Origin (2W)
    N0=-100000; // Grid Northing of True Origin (m)
    E0=400000;  // Grid Easting of True Origin (m)
    }
   else if (Area.substring(0,2)=='FI')
    { // Finnish KKJ International Ellipsoid
    F0=1.0;
    A1=6378388.000*F0;
    B1=6356911.946*F0;
    K0=0;
    Merid=21+3*(eval(Area.substring(2,3))-1);
    Form.Meridian.value='';
    L0=Merid*Deg2Rad;
    N0=0;
    E0=500000+1000000*eval(Area.substring(2,3));
    }
 else if (Area=='IE')
    { // Ireland (modified Airy Ellipsoid)
    F0=1.000035;
    A1=6377340.189*F0;
    B1=6356034.5*F0;
    K0=53.5*Deg2Rad;
    Merid=-8;
    Form.Meridian.value='';
    L0=Merid*Deg2Rad;
    N0=250000;
    E0=200000;
    }
 else if (Area=='SE')
    { // Sweden (Bessel Ellipsoid)
    F0=1.0;
    A1=6377397.155*F0;
    B1=6356078.963*F0;
    K0=0.0;
    Merid=15.8082777778;
    Form.Meridian.value='';
    L0=Merid*Deg2Rad;
    N0=0;
    E0=1500000;
    }
 else if (Area=='SE2')
    { // Sweden (GRS80)
    F0=1.00000564631;
    A1=6378137.0*F0;
    B1=6356752.3*F0;
    K0=0.0;
    Merid=15.8062819;
    Form.Meridian.value='';
    L0=Merid*Deg2Rad;
    N0=-667.968;
    E0=1500064.08;
    }
   else if (Area.substring(0,2)=='IT')
    { // Italy International Ellipsoid
    F0=0.9996;
    A1=6378388.000*F0;
    B1=6356911.946*F0;
    K0=0;
    Merid=9+6*(eval(Area.substring(2,3))-1);
    Form.Meridian.value='';
    L0=Merid*Deg2Rad;
    N0=0;
    if (Area.substring(2,3)=='1') E0=1500000; else E0=2520000;
    }
  else if (Area=='UTM1')
    { // UTM International Ellipsoid
    F0=0.9996;
    A1=6378388.000*F0;
    B1=6356911.946*F0;
    K0=0;
    N0=0;
    E0=500000;
    }
  else if (Area=='UTM2')
    { // UTM WGS84 Ellipsoid
    F0=0.9996;
    A1=6378137.0*F0;
    B1=6356752.3142*F0;
    K0=0;
    N0=0;
    E0=500000;
    }

  N1=(A1-B1)/(A1+B1); // n
  N2=N1*N1; N3=N2*N1;
  E2=((A1*A1)-(B1*B1))/(A1*A1); // e^2
  if (TM2LL)
    {
    /* yet to be implemented */
    }
  else
    {
    Deg=Form.LatDegrees.value; Min=Form.LatMinutes.value; Sec=Form.LatSeconds.value;
    AllBlank=(Deg=='')&&(Min=='')&&(Sec=='');
    if (Deg=='') Deg=0; if (Min=='') Min=0; if (Sec=='') Sec=0;
    if (AllBlank) Deg=91;
    Lat=1.0*abs(Deg)+abs(Min)/60.0+abs(Sec)/3600.0;
    if (Lat>90) {alert("Invalid Latitude"); OK=false; }
    South=((Form.NS.value.toUpperCase()=='S') && (Lat>0));
    if (South) Lat=-Lat;
    Deg=Form.LongDegrees.value; Min=Form.LongMinutes.value;
    Sec=Form.LongSeconds.value;
    AllBlank=(Deg=='')&&(Min=='')&&(Sec=='');
    if (Deg=='') Deg=0; if (Min=='') Min=0; if (Sec=='') Sec=0;
    if (AllBlank) Deg=181;
    West=(Form.EW.value.toUpperCase()=='W');
    Long=1.0*abs(Deg)+abs(Min)/60.0+abs(Sec)/3600.0;
    if (Long>180) {alert("Invalid Longitude"); OK=false; }
    if (West) Long=-Long;
    K=Lat*Deg2Rad; L=Long*Deg2Rad;
    SINK=sin(K); COSK=cos(K); TANK=SINK/COSK; TANK2=TANK*TANK;
    COSK2=COSK*COSK; COSK3=COSK2*COSK;
    K3=K-K0; K4=K+K0;

    if ((Area=='UTM1') || (Area=='UTM2'))
      {
      if (Form.AutoCM[0].checked)
        {
        Merid=floor((Long)/6)*6+3;
        if ((Lat>=72) && (Long>=0))
          {
          if (Long<9) Merid=3; else if (Long<21) Merid=15; else if (Long<33) Merid=27; else if (Long<42) Merid=39;
          }
        if ((Lat>=56) && (Lat<64))
          {
          if ((Long>=3) && (Long<12)) Merid=9;
          }
        MeridWest=Merid<0;
        if (MeridWest) {Form.MeridianEW.value='W';} else {Form.MeridianEW.value='E';}
        Form.Meridian.value=abs(Merid);
        L0=Merid*Deg2Rad; // Long of True Origin (3,9,15 etc)
        }
      else
        {
        Merid=Form.Meridian.value;
        if (Merid=='') {Merid=0; alert("You must enter a value for Central Meridian"); OK=false;}
        MeridWest=(Form.MeridianEW.value.toUpperCase()=='W');
        if (MeridWest) Merid=-Merid;
        L0=Merid*Deg2Rad; // Long of True Origin (3,9,15 etc)
        }
      }

    // ArcofMeridian
    J3=K3*(1+N1+1.25*(N2+N3));
    J4=sin(K3)*cos(K4)*(3*(N1+N2+0.875*N3));
    J5=sin(2*K3)*cos(2*K4)*(1.875*(N2+N3));
    J6=sin(3*K3)*cos(3*K4)*35/24*N3;
    M=(J3-J4+J5-J6)*B1;

    // VRH2
    Temp=1-E2*SINK*SINK;
    V=A1/sqrt(Temp);
    R=V*(1-E2)/Temp;
    H2=V/R-1.0;

    P=L-L0; P2=P*P; P4=P2*P2;
    J3=M+N0;
    J4=V/2*SINK*COSK;
    J5=V/24*SINK*(COSK3)*(5-(TANK2)+9*H2);
    J6=V/720*SINK*COSK3*COSK2*(61-58*(TANK2)+TANK2*TANK2);
    North=J3+P2*J4+P4*J5+P4*P2*J6;
    if (((Area=='UTM1') || (Area=='UTM2')) && South) North=North+10000000.0; // UTM S hemisphere
    J7=V*COSK;
    J8=V/6*COSK3*(V/R-TANK2);
    J9=V/120*COSK3*COSK2;
    J9=J9*(5-18*TANK2+TANK2*TANK2+14*H2-58*TANK2*H2);
    East=E0+P*J7+P2*P*J8+P4*P*J9;
    IEast=round(East); INorth=round(North); // should strictly be trunc
    Form.Easting.value=IEast;
    Form.Northing.value=INorth;
    }
  EastStr=''+abs(IEast); NorthStr=''+abs(INorth);
  while (EastStr.length<7) EastStr='0'+EastStr;
  while (NorthStr.length<7) NorthStr='0'+NorthStr;
  GR100km=eval(EastStr.substring(1,2)+NorthStr.substring(1,2));
  GRremainder=EastStr.substring(2,7)+' '+NorthStr.substring(2,7);
  if (Area=='UK')
    { // British Isles
    if (IEast<0 || INorth<0 || IEast>999999 || INorth>1499999)
      GR='outside British grid area';
    else
      {
      GR=Alpha100km.substring(GR100km,GR100km+1)+' '+GRremainder;
      HJ=(INorth>=1000000); TOJ=(IEast>=500000); ST=(INorth<500000);
      if (HJ)
        { if (TOJ) P='J'; else P='H'; }
      else
        {
        if (ST)
          { if (TOJ) P='T'; else P='S'; }
        else
          { if (TOJ) P='O'; else P='N'; }
        }
      GR=P+GR;
      }
    Form.GridRef.value=GR;
    }
  else if (Area.substring(0,2)=='FI')
    { // Finland
    ELow=1000000*eval(Area.substring(2,3));
    if (IEast<ELow || INorth<6600000 || IEast>(ELow+999999) || INorth>7799999)
      GR='outside Finnish zone area';
    else
      {
      GR=NorthStr+' : '+EastStr;
      }
    Form.GridRef.value=GR;
    }
  else if (Area=='IE')
    { // Ireland
    if (IEast<0 || INorth<0 || IEast>499999 || INorth>499999)
      GR='outside Irish grid area';
    else
      {
      GR=Alpha100km.substring(GR100km,GR100km+1)+' '+GRremainder;
      }
    Form.GridRef.value=GR;
    }
  else if (Area=='SE')
    { // Sweden (Bessel Ellipsoid)
    if (IEast<0 || INorth<0)
      GR='outside Swedish grid area';
    else
      GR=NorthStr+' '+EastStr;
    Form.GridRef.value=GR;
    }
  else if ((Area=='UTM1') || (Area=='UTM2'))
    { // UTM
    LongZone=(Merid-3)/6+31;
    if (LongZone % 1 != 0)
      GR='non-UTM central meridian';
    else
      {
      if (IEast<100000 || Lat<-80 || IEast>899999 || Lat>=84)
        GR='outside UTM grid area';
      else
        {
        Letters='ABCDEFGHJKLMNPQRSTUVWXYZ'
        Pos=round(Lat/8-0.5)+10+2;
        LatZone=Letters.substring(Pos,Pos+1);
        if (LatZone>'X') LatZone='X';
        Pos=round(abs(INorth)/100000-0.5);
        while (Pos>19) Pos=Pos-20;
        if (LongZone % 2 == 0)
         { Pos=Pos+5; if (Pos>19) Pos=Pos-20; }
        N100km=Letters.substring(Pos,Pos+1);
        Pos=GR100km/10-1;
        P=LongZone; while (P>3) P=P-3;
        Pos=Pos+((P-1)*8);
        E100km=Letters.substring(Pos,Pos+1);
        GR=LongZone+LatZone+E100km+N100km+' '+GRremainder;
        }
      }
    Form.GridRef.value=GR;
    }
  }
  if (!OK) ClearGridRef(Form);
  }

