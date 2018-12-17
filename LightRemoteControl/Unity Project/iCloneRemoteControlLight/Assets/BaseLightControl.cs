using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BaseLightControl : MonoBehaviour {

    RLTCPClient m_kTCP = null;
    Light m_kLight = null;

    string m_strLightType = "";

    // Use this for initialization
    void Start () {
        GameObject kNetObject = GameObject.Find( "NetworkManager" );
        if( kNetObject )
        {
            m_kTCP = kNetObject.GetComponent< RLTCPClient >();
        }
        m_kLight = GetComponent< Light >();
        if( m_kLight )
        {
            m_strLightType = m_kLight.type.ToString();
        }
    }
	
	// Update is called once per frame
	void Update () {
		
	}

    public void OnOff()
    {
        if( m_kLight )
        {
            m_kLight.enabled = !m_kLight.enabled;
            if( m_kTCP )
            {
                m_kTCP.SendData( "Type:" + m_strLightType + "," + "Power:" + m_kLight.enabled.ToString() );
            }
        }
    }

    public void SetIntensity( float fValue )
    {
        if( m_kLight )
        {
            m_kLight.intensity = fValue;
            if( m_kTCP )
            {
                m_kTCP.SendData( "Type:" + m_strLightType + "," + "Intensity:" + fValue.ToString() );
            } 
        }
    }
}
