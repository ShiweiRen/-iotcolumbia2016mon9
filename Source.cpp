#include "opencv2/objdetect/objdetect.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
using namespace std;
using namespace cv;

void detectAndDisplay(Mat frame);

String face_cascade_name = "G:\\Program Files (x86)\\OpenCV\\cascades.xml";
CascadeClassifier face_cascade;
string window_name = "Capture - Face detection";
RNG rng(12345);
int fnum = 0;

int xx1 = 90;
int xx3 = 450;
int xx5 = 800;

int yy1 = 20;
int yy3 = 100;
int yy5 = 400;



/** @function main */
int main(int argc, const char** argv)
{
	CvCapture* capture;
	Mat frame;
	//-- 1. Load the cascades
	if (!face_cascade.load(face_cascade_name)) { printf("--(!)Error loading\n"); return -1; };
	//-- 2. Read the video stream
	capture = cvCaptureFromCAM(0);
	//capture = cvCaptureFromFile(".\\IMG_1316.MOV");
	if (capture)
	{
		while (true)
		{
			frame = cvQueryFrame(capture);
			//-- 3. Apply the classifier to the frame
			if (!frame.empty())
			{
				flip(frame, frame, -1);
				detectAndDisplay(frame);
			}
			else
			{
				printf(" --(!) No captured frame -- Break!"); break;
			}
			int c = waitKey(10);
			if ((char)c == 'c') { break; }
		}
	}
	return 0;
}
/** @function detectAndDisplay */
void detectAndDisplay(Mat frame)
{
	std::vector<Rect> faces;
	Mat frame_gray;
	cvtColor(frame, frame_gray, CV_BGR2GRAY);
	equalizeHist(frame_gray, frame_gray);
	//-- Detect faces
	face_cascade.detectMultiScale(frame_gray, faces, 1.1, 4, 0 | CV_HAAR_SCALE_IMAGE, Size(130, 130));
	

	bool isEmpty[4] = { true,true,true,true };
	int count = 0;

	Rect* positions = new Rect[4];
	positions[2] = Rect(xx1, yy3, 300, 300);
	positions[3] = Rect(xx5, yy3, 300, 300);
	positions[0] = Rect(xx3, yy1, 300, 250);
	positions[1] = Rect(xx3, yy5, 300, 300);

	Point* centers = new Point[faces.size()];
	
	for (size_t i = 0; i < faces.size(); i++)
	{
		rectangle(frame, faces[i], Scalar(0, 255, 0));
		centers[i] = Point(int(faces[i].x + faces[i].width*0.5), int(faces[i].y + faces[i].height*0.5));
		//cout << "X:" << center.x << "  Y:" << center.y << endl;
		circle(frame, centers[i], 3, Scalar(255, 0, 0), -1, 8, 0);
	}

	for (int i = 0; i < 4; i++) 
	{
		for (size_t j = 0; j < faces.size(); j++)
		{
			if (positions[i].contains(centers[j])) 
			{
				isEmpty[i] = false;
				break;
			}
		}
	}

	for (int i = 0; i < 4; i++) 
	{
		if (isEmpty[i])
		{
			rectangle(frame, positions[i], Scalar(255, 0, 0));
		}else {
			rectangle(frame, positions[i], Scalar(0, 0, 255));
			count++;
		}
	}
	cout << count << endl;
	imshow(window_name, frame);
	char str[30];
	sprintf(str, "%s%d%s", "./result/", fnum++, ".jpg");
	imwrite(str, frame);
}