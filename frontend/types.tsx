/**
 * Learn more about using TypeScript with React Navigation:
 * https://reactnavigation.org/docs/typescript/
 */

import { BottomTabScreenProps } from '@react-navigation/bottom-tabs';
import { CompositeScreenProps, NavigatorScreenParams } from '@react-navigation/native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';

declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}

export type RootStackParamList = {
  Root: NavigatorScreenParams<RootTabParamList> | undefined;
  AppInfo: undefined;
  NotFound: undefined;
  LiveFormAnalyser: undefined;
  FormReview: { videoUri: string, formData: any };
  PostSetSummary: FinalSummary;
};

export type RootStackScreenProps<Screen extends keyof RootStackParamList> = NativeStackScreenProps<
  RootStackParamList,
  Screen
>;

export type FinalSummary = {
  goodReps: number,
  badReps: number,
  mistakesMade: {
    rep: number,
    mistakes: string[],
  }[],
  finalComments: string,
}

export type RootTabParamList = {
  Menu: undefined;
  Settings: undefined;
  AppInfo: undefined;
  FormReview: { videoUri: string, formData: any };
  PostSetSummary: FinalSummary;
};

export type RootTabScreenProps<Screen extends keyof RootTabParamList> = CompositeScreenProps<
  BottomTabScreenProps<RootTabParamList, Screen>,
  NativeStackScreenProps<RootStackParamList>
>;
