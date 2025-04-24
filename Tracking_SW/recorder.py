import cv2 
  
  
def main(): 
    
    # reading the input 
    cap = cv2.VideoCapture(0) 
  
    output = cv2.VideoWriter( 
        "output.mp4", cv2.VideoWriter_fourcc(*'mp4v'), 30, (1080, 1920)) 
  
    while(True): 
        ret, frame = cap.read() 
        if(ret): 
              
            # adding rectangle on each frame               
            # writing the new frame in output 
            output.write(frame) 
            cv2.imshow("output", frame) 
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break
  
    cv2.destroyAllWindows() 
    output.release() 
    cap.release() 
  
  
if __name__ == "__main__":
    main()  