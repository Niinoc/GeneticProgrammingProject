/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.geneticprogramming;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * A class for writing log-data to files.
 * Usage:     Log.println("dat", myDataString);          // does a flush, so use this !!
 * Log.flush("dat")
 * Log.close("dat");   // seems not to be necessary 
 * Note that    Log.writer("dat").println(myDataString);  does not flush !
 * @author Peter
 */
public class Log extends Global{

    static Map<String, PrintWriter> writers = new HashMap<>();


    public static String fileNameEnding2fileName(String fileNameEnding){
        return logFolderPath + logFileNamePrefix + fileNameEnding + logFileNamePostfix;
    }

    public static void createLogFolder() {
        if (!logFolderPath.endsWith("/")) {
            logFolderPath += "/";
        }
        Path logFolder = Paths.get(logFolderPath);
        if (!Files.exists(logFolder)) {
            try {
                Files.createDirectories(logFolder);
            } catch (IOException e) {
                e.printStackTrace();  // Handle error appropriately
            }
        }
    }

    public static PrintWriter writer(String fileNameEnding) {
        String fileName = fileNameEnding2fileName(fileNameEnding);
        if (writers.containsKey(fileName)) {
            return writers.get(fileName);
        }
        try {
            // else open the new file
            writers.put(fileName, new PrintWriter(fileName, "UTF-8"));
        } catch (FileNotFoundException ex) {
            Logger.getLogger(Log.class.getName()).log(Level.SEVERE, null, ex);
        } catch (UnsupportedEncodingException ex) {
            Logger.getLogger(Log.class.getName()).log(Level.SEVERE, null, ex);
        }
        return writers.get(fileName);

    }
    /***
     * Write a string to a log-file.
     * The actual file name depends on fileNamePrefix and fileNameSuffix.
     * @param fileNameEnding
     * @param message to be written to the file.
     */
    public static void println(String fileNameEnding, String message){
        writer(fileNameEnding).println(message);
        flush(fileNameEnding);  // brutal, but that's how it is ...
    }

    public static void close(String fileNameEnding){
        String fileName = fileNameEnding2fileName(fileNameEnding);
        if (writers.containsKey(fileName)) {
            writers.get(fileName).close();
            writers.remove(fileName);
        }
    }

    public static void flush(String fileNameEnding){
        String fileName = fileNameEnding2fileName(fileNameEnding);
        if (writers.containsKey(fileName)) {
            writers.get(fileName).flush();
        }
    }

}
