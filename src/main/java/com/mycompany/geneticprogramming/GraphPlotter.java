package com.mycompany.geneticprogramming;

import javax.swing.*;
import java.awt.*;
import java.util.Arrays;

public class GraphPlotter extends JPanel {

    //<editor-fold desc="Attribute">
    private static final int WIDTH = 800;
    private static final int HEIGHT = 600;
    private static final int MARGIN = 50;

    private double[] inputs;
    private double[] outputs;
    private double[] expectedOutputs;
    private double minInput = -10;
    private double minOutput = -10;
    private double xScale;
    private double yScale;
    //</editor-fold>

    public GraphPlotter(double[] fitnessInputs, double[] outputs, double[] fitnessOutputs) {      //TODO -> braucht inputs und outputs der fitnessregression

        this.inputs = fitnessInputs;
        this.outputs = outputs;
        this.expectedOutputs = fitnessOutputs;

        // Determine the scale for x-axis
        this.minInput = -3; // Mindestwert für x-Achse
        double maxInput = 3;  // Höchstwert für x-Achse
        this.xScale = (WIDTH - 2 * MARGIN) / (maxInput - minInput);

        // Determine the scale for y-axis
        this.minOutput = Math.min(Arrays.stream(outputs).min().orElse(0), Arrays.stream(expectedOutputs).min().orElse(0));
        double maxOutput = Math.max(Arrays.stream(outputs).max().orElse(0), Arrays.stream(expectedOutputs).max().orElse(0));
        this.yScale = (HEIGHT - 2 * MARGIN) / (maxOutput - minOutput);


        //<editor-fold desc="Frame">
        JFrame frame = new JFrame("Graph Plotter");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.getContentPane().add(this);
        frame.setSize(800, 600);                                                                //TODO gott warum -> bitte variable
        frame.setLocationRelativeTo(null); // Zentrieren Sie das JFrame auf dem Bildschirm
        frame.setVisible(true); // Zeigen Sie das JFrame an
        //</editor-fold>

    }


    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2d = (Graphics2D) g;

        // Draw background
        g2d.setColor(Color.WHITE);
        g2d.fillRect(0, 0, WIDTH, HEIGHT);

        // Enable anti-aliasing for smoother lines
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        // Draw axes
        g2d.setColor(Color.BLACK);
        g2d.drawLine(MARGIN, HEIGHT / 2, WIDTH - MARGIN, HEIGHT / 2); // x-axis
        g2d.drawLine(WIDTH / 2, MARGIN, WIDTH / 2, HEIGHT - MARGIN); // y-axis

        // Plot functions
        plotFunctions(g2d);
    }

    private void plotFunctions(Graphics2D g2d) {

        // Plot expected outputs
        g2d.setColor(Color.BLUE);
        plotLine(g2d, inputs, expectedOutputs);

        // Plot calculated outputs
        g2d.setColor(Color.RED);
        plotLine(g2d, inputs, outputs);

        g2d.setColor(Color.GREEN);
        plotFitnessCases(g2d);
    }

    private void plotFitnessCases(Graphics2D g2d) {
        g2d.setColor(Color.GREEN);
        for (int i = 0; i < inputs.length; i++) {
            double x = (MARGIN + (inputs[i] * xScale - minInput * xScale));
            double y = (HEIGHT - MARGIN - (outputs[i] - minOutput) * yScale);
            g2d.fillOval((int) (x - 2), (int) (y - 2), 4, 4);
        }

    }

    private void plotLine(Graphics2D g2d, double[] inputs, double[] values) {
        for (int i = 0; i < inputs.length - 1; i++) {
            int x1 = (int) (MARGIN + (inputs[i] - minInput) * xScale);
            int y1 = (int) (HEIGHT - MARGIN - (values[i] - minOutput) * yScale);
            int x2 = (int) (MARGIN + (inputs[i + 1] - minInput) * xScale);
            int y2 = (int) (HEIGHT - MARGIN - (values[i + 1] - minOutput) * yScale);
            g2d.drawLine(x1, y1, x2, y2);
        }
    }
}
