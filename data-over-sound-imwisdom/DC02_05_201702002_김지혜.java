package com.example.sound.devicesound;

import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.os.Bundle;
import android.renderscript.ScriptGroup;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.Toast;

import org.apache.commons.math3.analysis.function.Max;
import org.apache.commons.math3.complex.Complex;
import org.apache.commons.math3.transform.*;
import org.apache.commons.math3.util.DoubleArray;

import java.io.BufferedInputStream;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.ObjectInputStream;
import java.io.UnsupportedEncodingException;
import java.lang.reflect.Array;
import java.nio.Buffer;
import java.nio.ByteBuffer;
import java.nio.DoubleBuffer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;


public class Listentone extends AppCompatActivity {

    int HANDSHAKE_START_HZ = 4096;
    int HANDSHAKE_END_HZ = 5120 + 1024;

    int START_HZ = 1024;
    int STEP_HZ = 256;
    int BITS = 4;

    int FEC_BYTES = 4;

    private int mAudioSource = MediaRecorder.AudioSource.MIC;
    private int mSampleRate = 44100;
    private int mChannelCount = AudioFormat.CHANNEL_IN_MONO;
    private int mAudioFormat = AudioFormat.ENCODING_PCM_16BIT;
    private float interval = 0.1f;

    private int mBufferSize = AudioRecord.getMinBufferSize(mSampleRate, mChannelCount, mAudioFormat);

    public AudioRecord mAudioRecord = null;
    int audioEncodig;
    boolean startFlag;
    FastFourierTransformer transform;

    public Listentone(){

        transform = new FastFourierTransformer(DftNormalization.STANDARD);
        startFlag = false;
        mAudioRecord = new AudioRecord(mAudioSource, mSampleRate, mChannelCount, mAudioFormat, mBufferSize);
        mAudioRecord.startRecording();
    }

    //decode.py와 같이 구현
    //소리를 변환해서 hz로 만들고 decode
    public void PreRequest() {

        ArrayList<Double> packet = new ArrayList<Double>();
        int blocksize = findPowerSize((int) (long) Math.round(interval / 2 * mSampleRate));

        while(true) {
            //read
            short[] buffer = new short[blocksize];
            int bufferedReadResult = mAudioRecord.read(buffer, 0, blocksize);

            if (bufferedReadResult == -1) continue;

            double[] double_buffer = new double[blocksize];

            for (int i = 0; i < buffer.length; i++) {
                double_buffer[i] = (double) buffer[i];
            }

            double dom = findFrequency(double_buffer);
            Log.d("dom : ", Double.toString(dom));


            if (startFlag && match(dom, HANDSHAKE_END_HZ)) {
                byte[] byte_stream = new byte[packet.size()];
                byte_stream = extract_packet(packet);

                Log.d("extract : ",Arrays.toString(byte_stream));
                try {
                    String ss = new String(byte_stream, "UTF-8");

                    Log.d("string : ", ss);

                } catch (UnsupportedEncodingException e) {
                    Log.d("no", "no");
                    break;
                }
                packet = new ArrayList<Double>();
                startFlag = false;

            } else if (startFlag)
                packet.add(dom);

            else if (match(dom, HANDSHAKE_START_HZ))
                startFlag = true;

        }
    }
    private int findPowerSize(int a)
    {
        int i=2;
        for(;i<a;i*=2);

        if(Math.abs(i/2-a)>Math.abs(i-a)) return i;
        else return i/2;
    }
    private byte[] extract_packet(ArrayList<Double> freqs)
    {
        ArrayList<Double> newfreqs = new ArrayList<Double>();
        for(int i=0;i<freqs.size();i+=2)
            newfreqs.add(freqs.get(i));

        //bit_chunk 만들기
        ArrayList<Integer> bit_chunks = new ArrayList<Integer>();

        for(int i=0;i<newfreqs.size();i++)
            bit_chunks.add((int)Math.round((newfreqs.get(i)-START_HZ)/STEP_HZ));

        if(bit_chunks.size()>0)
            bit_chunks.remove(0);
        for(int i=0;i<bit_chunks.size();i++)
        {
            if(bit_chunks.get(i)>=Math.pow(2, BITS) || bit_chunks.get(i)<0 || i>0 && bit_chunks.get(i)==bit_chunks.get(i-1))
                bit_chunks.remove(i);
        }

        bit_chunks = decode_bitchunks(BITS, bit_chunks);

        //bytearray
        byte[] byteArray = new byte[bit_chunks.size()];
        Integer[] bit_chunks_array = new Integer[bit_chunks.size()];
        bit_chunks_array = bit_chunks.toArray(bit_chunks_array);

        for(int i=0;i<bit_chunks_array.length;i++)
        {
            byteArray[i] = bit_chunks_array[i].byteValue();
        }

        return byteArray;

    }
    private ArrayList decode_bitchunks(int chunk_bits, ArrayList<Integer> chunks)
    {
        ArrayList out_byte = new ArrayList();

        int next_read_chunk = 0;
        int next_read_bit = 0;

        int abyte = 0;
        int bits_left = 8;

        int can_fill;
        int to_fill;
        int offset;
        int shifted;

        while(next_read_chunk < chunks.size())
        {
            can_fill = chunk_bits - next_read_bit;
            to_fill = Math.min(bits_left, can_fill);
            offset = chunk_bits - next_read_bit - to_fill;
            abyte <<= to_fill;
            shifted = chunks.get(next_read_chunk) & ((( 1 << to_fill) - 1 ) << offset);
            abyte |= shifted >> offset;
            bits_left -= to_fill;
            next_read_bit += to_fill;

            if(bits_left <= 0)
            {
                out_byte.add(abyte);
                abyte = 0;
                bits_left = 8;
            }

            if(next_read_bit >= chunk_bits)
            {
                next_read_chunk += 1;
                next_read_bit -= chunk_bits;
            }
        }

        return out_byte;
    }
    private boolean match(double a, int b)
    {
        return Math.abs(a-b) <20;
    }
    private double findFrequency(double[] toTransform)
    {
        int len = toTransform.length;
        double[] real = new double[len];
        double[] img = new double[len];
        double realNum;
        double imgNum;
        double[] mag = new double[len];

        Complex[] complexes = transform.transform(toTransform, TransformType.FORWARD);
        Double[] freq = this.fftfreq(complexes.length, 1);

        for(int i=0; i<complexes.length ; i++) {
            realNum = complexes[i].getReal();
            imgNum = complexes[i].getImaginary();
            mag[i] = Math.sqrt((realNum * realNum) + (imgNum * imgNum));
        }

        int maxIndex = 0;

        for(int i=1; i<complexes.length; i++)
            if (mag[i] > mag[maxIndex]) maxIndex = i;

        double peak_freq = freq[maxIndex];

        return Math.abs(peak_freq * mSampleRate);
    }

    private Double[] fftfreq(int length, int i) {

        Double[] freq = new Double[length];
        double plus = 0.0;
        if(length%2==0)
        {
            for(int j=0;j<length;j++)
            {
                freq[j] = plus;
                plus += 1;
                if (freq[j] == length / 2 - 1) plus = (double) -length / 2;
                freq[j]/=(length*i);
            }
        }
        else
        {
            for(int j=0;j<length;j++)
            {
                freq[j] = plus;
                plus+=1;
                if(freq[j]==(length-1)/2) plus = (double)-(length-1)/2;
                freq[j]/=(length*i);
            }
        }

        return freq;
    }


}
