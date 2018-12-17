using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ConnectButtonImageControl : MonoBehaviour {
    public Sprite DisableImage = null;
    public Sprite ActivedImage = null;
    public Sprite NormalImage = null;
    public UnityEngine.UI.Text InputFieldText = null;
    private UnityEngine.UI.Image m_kCurrentImage = null;
    private RLTCPClient m_kTCP = null;
    private bool m_bActive = false;

    // Use this for initialization
    void Start () {
		GameObject kNetObject = GameObject.Find( "NetworkManager" );
        if( kNetObject )
        {
            m_kTCP = kNetObject.GetComponent< RLTCPClient >();
        }
        m_kTCP.SetStatusChangedCallBack( ( bool bStatus ) =>
        {
            m_bActive = bStatus;
        } );
        m_kCurrentImage = gameObject.GetComponent<Image>();
    }
	
	// Update is called once per frame
	void Update () {
        if( m_bActive && m_kCurrentImage.sprite != ActivedImage )
        {
            m_kCurrentImage.sprite = ActivedImage;
        }
        else if( string.IsNullOrEmpty( InputFieldText.text ) && m_kCurrentImage.sprite != DisableImage )
        {
            m_kCurrentImage.sprite = DisableImage;
        }
        else if( !string.IsNullOrEmpty( InputFieldText.text ) && !m_bActive && m_kCurrentImage.sprite != NormalImage )
        {
            m_kCurrentImage.sprite = NormalImage;
        }
	}
}
