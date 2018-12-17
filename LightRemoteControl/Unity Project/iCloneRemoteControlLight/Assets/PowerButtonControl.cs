using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class PowerButtonControl : MonoBehaviour {
    public Sprite PowerOnImage = null;
    public Sprite PowerOffImage = null;
    public Light TargetLight = null;
    private UnityEngine.UI.Image m_kCurrentImage = null;
    // Use this for initialization
    void Start () {
        m_kCurrentImage = gameObject.GetComponent<Image>();
    }
	
	// Update is called once per frame
	void Update () {
		if( m_kCurrentImage != null && TargetLight != null )
        {
            if( TargetLight.enabled && m_kCurrentImage.sprite != PowerOnImage )
            {
                m_kCurrentImage.sprite = PowerOnImage;
            }
            else if( !TargetLight.enabled && m_kCurrentImage.sprite != PowerOffImage )
            {
                m_kCurrentImage.sprite = PowerOffImage;
            }
        }
	}
}
