using System;
using System.Collections;
using System.Collections.Generic;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class RLTCPClient : MonoBehaviour
{

    private Thread m_kReceiveThread;
    private TcpClient m_kClient;
    private string m_strFromServerData;
    private string m_strIp = "";
    private int m_nPort = 7701;
    // Use this for initialization
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {

    }

    public void SetIp( string strIp )
    {
        m_strIp = strIp;
    }

    public void SetPort( int nIp )
    {
        m_nPort = nIp;
    }

    public void ConnectToTcpServer()
    {
        try
        {
            m_kClient = new TcpClient( m_strIp, m_nPort );
            m_kReceiveThread = new Thread( new ThreadStart( ListenForData ) );
            m_kReceiveThread.IsBackground = true;
            m_kReceiveThread.Start();
        }
        catch( Exception e )
        {
            Debug.Log( "Connect To TcpServer exception " + e );
        }
    }

    public void ListenForData()
    {
        try
        {
            Byte[] kBytes = new Byte[ 1024 ];
            while( true )
            {
                using( NetworkStream kStream = m_kClient.GetStream() )
                {
                    int length;
                    while( ( length = kStream.Read( kBytes, 0, kBytes.Length ) ) != 0 )
                    {
                        var kIncommingData = new byte[ length ];
                        Array.Copy( kBytes, 0, kIncommingData, 0, length );
                        m_strFromServerData += Encoding.ASCII.GetString( kIncommingData ) + "\r\n";
                        Debug.Log( "server message received as: " + m_strFromServerData );
                    }
                }
            }
        }
        catch( SocketException socketException )
        {
            Debug.Log( "Socket exception: " + socketException );
        }
    }

    public void SendData( string strData )
    {
        if( m_kClient == null )
        {
            return;
        }
        try
        {
            NetworkStream kStream = m_kClient.GetStream();
            if( kStream.CanWrite )
            {
                byte[] kData = Encoding.ASCII.GetBytes( strData );
                kStream.Write( kData, 0, kData.Length );
            }
        }
        catch( SocketException socketException )
        {
            Debug.Log( "Socket exception: " + socketException );
        }
    }
}
